"""
agent.py

This is the orchestrator: the only file that implements the agent's
decision loop AND its conversation memory. It does not know HOW to call
Gemini (that's llm.py) or HOW the calculator/search tools work internally
(that's tools.py) — it just decides WHEN to use them and passes
information between them.

Two kinds of tools are offered together in every request:

1. calculator (client-side) — Gemini asks US to run it. We see this as
   an entry in response.function_calls, execute the real Python
   function ourselves, and send the result back in a follow-up call.

2. google_search (server-side / built-in) — Gemini runs this ITSELF,
   before returning a response. It never appears in
   response.function_calls. We only ever read the finished answer plus
   optional grounding_metadata describing what was searched/cited.

Conversation memory:
Each ResearchAgent instance holds its own `history` list in memory. Every
user message, every tool call/result, and every model reply gets appended
to it, and the *entire* history is re-sent to Gemini on every turn. This
memory only lives as long as the ResearchAgent object does.
"""

from google.genai import types

from app.llm import generate
from app.tools import calculator, calculator_declaration, google_search_tool

# Map tool names (as Gemini will refer to them) to the real Python
# functions that implement them. Only client-side tools go here —
# google_search has no Python implementation, so it is never in this map.
AVAILABLE_TOOLS = {
    "calculator": calculator,
}

# Gemini 3 requires built-in tools and custom function tools to be
# declared together inside ONE Tool object, not as two separate Tool
# entries in the list. We reuse the existing google_search_tool's
# `.google_search` field and the existing calculator_declaration,
# rather than redefining either from scratch.
COMBINED_TOOL = types.Tool(
    google_search=google_search_tool.google_search,
    function_declarations=[calculator_declaration],
)

# Required to enable combining a built-in tool (Google Search) with a
# custom function tool (calculator) in the same request.
SERVER_SIDE_TOOL_CONFIG = types.ToolConfig(
    include_server_side_tool_invocations=True
)


def _format_sources(response) -> str:
    """
    Build a short "Sources:" section from a Gemini response's grounding
    metadata, if any is present.

    This is intentionally defensive: grounding metadata may be missing
    entirely (e.g. Gemini didn't search), and individual source entries
    may be missing a title or URL. In all of those cases, this function
    safely returns an empty string instead of raising an error.

    Args:
        response: A Gemini response object (from llm.generate()).

    Returns:
        A string like "\n\nSources:\n- Title: https://..." or "" if
        there are no usable sources to show.
    """
    try:
        candidate = response.candidates[0]
    except (IndexError, AttributeError, TypeError):
        return ""

    grounding_metadata = getattr(candidate, "grounding_metadata", None)
    if not grounding_metadata:
        return ""

    grounding_chunks = getattr(grounding_metadata, "grounding_chunks", None)
    if not grounding_chunks:
        return ""

    lines = []
    for chunk in grounding_chunks:
        web = getattr(chunk, "web", None)
        if not web:
            continue

        uri = getattr(web, "uri", None)
        if not uri:
            # No URL means this source isn't usable/linkable — skip it.
            continue

        title = getattr(web, "title", None) or uri
        lines.append(f"- {title}: {uri}")

    if not lines:
        return ""

    return "\n\nSources:\n" + "\n".join(lines)


class ResearchAgent:
    """
    An agent that remembers the conversation for as long as this object
    exists. Create one instance per session (e.g. once in main.py) and
    keep calling `run()` on it — do not create a new instance per message,
    or memory will be lost.
    """

    def __init__(self):
        # The full conversation so far, as a list of types.Content objects.
        # This is short-term, in-memory-only history: it disappears the
        # moment this ResearchAgent object is destroyed (e.g. on program exit).
        self.history = []

    def run(self, user_input: str) -> str:
        """
        Run one full turn of the agent loop for a single user message,
        using and updating this agent's conversation history.

        Gemini decides for itself, per message, whether Google Search is
        actually needed — offering the tool does not force its use.

        Args:
            user_input: The user's question or request, as plain text.

        Returns:
            The agent's final answer, as plain text. If the answer was
            grounded with Google Search, a "Sources:" section is appended.
        """
        # Add the user's new message to the ongoing conversation.
        self.history.append(
            types.Content(role="user", parts=[types.Part(text=user_input)])
        )

        # Step 1: send the FULL conversation so far to Gemini, offering
        # both the calculator and Google Search together.
        response = generate(
            self.history,
            tools=[COMBINED_TOOL],
            tool_config=SERVER_SIDE_TOOL_CONFIG,
        )

        # Step 2: did Gemini ask US to run a client-side tool (calculator)?
        # Note: Google Search, even if Gemini used it, never shows up here —
        # it's resolved server-side before this response ever reaches us.
        if not response.function_calls:
            # Step 3: no calculator call needed. Store Gemini's complete
            # reply Content in history exactly as returned (never modified
            # or stripped down), so future turns have full context.
            self.history.append(response.candidates[0].content)

            # Sources are shown to the user but never stored in history —
            # they're display-only, not part of the conversation Gemini needs.
            return response.text + _format_sources(response)

        # Step 4: Gemini wants to call a tool. We only handle the first
        # requested call for now, since we only have one client-side tool.
        function_call = response.function_calls[0]
        tool_name = function_call.name
        tool_args = function_call.args

        # Record Gemini's function-call turn in history before we act on it.
        self.history.append(response.candidates[0].content)

        if tool_name not in AVAILABLE_TOOLS:
            return f"Error: the model requested an unknown tool '{tool_name}'."

        # Actually run the real Python function with the arguments Gemini gave us.
        tool_function = AVAILABLE_TOOLS[tool_name]
        tool_result = tool_function(**tool_args)

        # Step 5: record the tool's result in history, in the format
        # Gemini expects for a function response. The id must match the
        # originating function_call so Gemini can correctly map the result
        # back to the correct request (required for Gemini 3 combined
        # tool/context-circulation mode).
        self.history.append(
            types.Content(
                role="user",
                parts=[
                    types.Part.from_function_response(
                        id=function_call.id,
                        name=function_call.name,
                        response=tool_result,
                    )
                ],
            )
        )

        # Step 6: send the updated history (now including the tool result)
        # back to Gemini, still offering both tools, to get a final answer.
        final_response = generate(
            self.history,
            tools=[COMBINED_TOOL],
            tool_config=SERVER_SIDE_TOOL_CONFIG,
        )

        # Record Gemini's final answer Content in history, unmodified.
        self.history.append(final_response.candidates[0].content)

        return final_response.text + _format_sources(final_response)
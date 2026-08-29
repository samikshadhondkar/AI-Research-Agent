"""
llm.py

This is the ONLY file in the project that talks directly to the Gemini API.
Every other file (agent.py, main.py, tools.py) should go through the
`generate()` function below instead of importing google.genai themselves.

Why keep it isolated like this?
If we ever change LLM providers, or change how we call Gemini, this is the
only file that needs to be touched. This is also why API error handling
lives here: this is the only place that knows what a raw Gemini API error
looks like, so it's the right place to turn it into a safe, clear message
before anything else in the app ever sees it.
"""

import os

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

# Keep the model name in exactly one place so it's easy to change later.
MODEL_NAME = "gemini-3.5-flash-lite"


# ---------------------------------------------------------------------------
# Setup: load the API key and create the client
# ---------------------------------------------------------------------------

# Reads the .env file (if present) and loads its values into the environment.
load_dotenv()

_api_key = os.environ.get("GEMINI_API_KEY")

if not _api_key:
    raise RuntimeError(
        "GEMINI_API_KEY is not set.\n"
        "Fix this by:\n"
        "  1. Copying .env.example to a new file named .env\n"
        "  2. Adding your Gemini API key to that .env file, e.g.:\n"
        "     GEMINI_API_KEY=your-key-here\n"
        "You can get a free key from Google AI Studio: "
        "https://aistudio.google.com/apikey"
    )

# Create ONE client and reuse it for every request in the app.
_client = genai.Client(api_key=_api_key)


# ---------------------------------------------------------------------------
# Public function — this is what the rest of the app will call
# ---------------------------------------------------------------------------

def generate(contents, tools=None, tool_config=None):
    """
    Send a request to Gemini and return the raw response object.

    Args:
        contents: The conversation/content to send to the model.
                  Can be a plain string, or a list of types.Content
                  objects representing the conversation so far.
        tools: Optional list of tool declarations. llm.py has no
               knowledge of what specific tools exist (calculator,
               Google Search, etc.) — that decision belongs to agent.py.
        tool_config: Optional types.ToolConfig. Only needed for certain
               tool setups (e.g. enabling server-side tool invocations
               when combining a built-in tool with a custom function
               tool). If not provided, no tool_config is sent at all,
               preserving existing behavior exactly as before.

    Returns:
        The response object returned by the Gemini SDK. Callers can read
        `response.text` for plain text, or `response.function_calls` once
        tools are added.

    Raises:
        RuntimeError: With a short, safe, user-facing message if the
            Gemini API call fails for any reason (quota exhausted, auth
            failure, network issue, etc.). The original exception details
            (which can include internal error payloads) are never exposed.
    """
    config_kwargs = {
        "tools": tools,
        # We handle tool calls ourselves, step by step, instead of letting
        # the SDK silently call functions for us. This is intentional:
        # it's how we learn what an "agent loop" actually does.
        "automatic_function_calling": types.AutomaticFunctionCallingConfig(
            disable=True
        ),
    }

    # Only include tool_config if the caller actually provided one, so
    # existing calls (which don't pass it) behave exactly as before.
    if tool_config is not None:
        config_kwargs["tool_config"] = tool_config

    config = types.GenerateContentConfig(**config_kwargs)

    try:
        response = _client.models.generate_content(
            model=MODEL_NAME,
            contents=contents,
            config=config,
        )
    except errors.APIError as api_error:
        # google-genai's own error type. It reliably exposes `.code`
        # (HTTP status, e.g. 429) and `.status` (e.g. "RESOURCE_EXHAUSTED",
        # "UNAUTHENTICATED"), so we can react to it without needing to
        # parse or expose the raw error payload.
        code = getattr(api_error, "code", None)
        status = (getattr(api_error, "status", "") or "").upper()

        if code == 429 or status == "RESOURCE_EXHAUSTED":
            raise RuntimeError(
                "Gemini API quota is currently exhausted. "
                "Please try again later."
            ) from None

        if code in (401, 403) or status in ("UNAUTHENTICATED", "PERMISSION_DENIED"):
            raise RuntimeError(
                "Gemini API authentication failed. "
                "Please check your API key."
            ) from None

        # Any other API error (bad request, server error, etc.) — keep the
        # message generic and safe rather than exposing internal details.
        raise RuntimeError(
            "The Gemini API could not be reached. Please try again."
        ) from None
    except Exception:
        # Anything else — e.g. no internet connection, DNS failure — that
        # never even made it to a Gemini API response. Same safe message,
        # since the underlying cause isn't something the user can act on
        # beyond "try again".
        raise RuntimeError(
            "The Gemini API could not be reached. Please try again."
        ) from None

    return response
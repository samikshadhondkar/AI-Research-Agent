"""
tools.py

Defines the tools our agent can use.

There are two different kinds of tools here:

1. Client-side tools (e.g. calculator): WE own the implementation. Each
   one has two parts that must stay in sync — a real Python function that
   does the work, and a Gemini FunctionDeclaration describing it. Gemini
   only ever requests a call; our own code (in agent.py) actually runs
   the function and sends the result back.

2. Server-side / built-in tools (e.g. Google Search): GEMINI owns the
   implementation. We only provide a declaration saying "this capability
   exists" — there is no Python function for us to write, and no result
   for us to compute or send back. Gemini executes the search itself and
   returns an already-finished, grounded answer.
"""

from google.genai import types

# ---------------------------------------------------------------------------
# Client-side tool: calculator
# ---------------------------------------------------------------------------

def calculator(operation: str, a: float, b: float) -> dict:
    """
    Perform a basic arithmetic operation on two numbers.

    Supported operations:
        add      -> a + b
        subtract -> a - b
        multiply -> a * b
        divide   -> a / b
        power    -> a raised to the power of b (a ** b)
        root     -> the b-th root of a (e.g. root(27, 3) = 3)

    Args:
        operation: One of "add", "subtract", "multiply", "divide",
                   "power", "root".
        a: The first number. For "root", this is the number you are
           finding the root of.
        b: The second number. For "root", this is the root degree
           (e.g. 2 for square root, 3 for cube root).

    Returns:
        A dictionary. On success: {"result": <number>}.
        On failure: {"error": "<description of what went wrong>"}.
        This function never raises an exception for bad input — it always
        returns one of the two dictionary shapes above.
    """
    if operation == "add":
        return {"result": a + b}

    if operation == "subtract":
        return {"result": a - b}

    if operation == "multiply":
        return {"result": a * b}

    if operation == "divide":
        if b == 0:
            return {"error": "Cannot divide by zero."}
        return {"result": a / b}

    if operation == "power":
        return {"result": a ** b}

    if operation == "root":
        if b == 0:
            return {"error": "Root degree cannot be zero."}
        if a < 0 and b % 2 == 0:
            return {"error": "Cannot take an even root of a negative number."}
        # Handle negative numbers with odd roots correctly (e.g. root(-27, 3) = -3)
        if a < 0:
            return {"result": -((-a) ** (1 / b))}
        return {"result": a ** (1 / b)}

    return {"error": f"Unknown operation: '{operation}'."}


# The Gemini tool declaration for calculator().
#
# This must be kept in sync with calculator()'s parameters above.
# If you add/remove/rename a parameter in calculator(), update this too.
calculator_declaration = types.FunctionDeclaration(
    name="calculator",
    description=(
        "Performs a basic arithmetic operation (add, subtract, multiply, "
        "divide, power, or root) on two numbers and returns the result. "
        "For 'root', 'a' is the number and 'b' is the root degree "
        "(e.g. a=27, b=3 computes the cube root of 27, which is 3)."
    ),
    parameters=types.Schema(
        type="OBJECT",
        properties={
            "operation": types.Schema(
                type="STRING",
                description="The operation to perform.",
                enum=["add", "subtract", "multiply", "divide", "power", "root"],
            ),
            "a": types.Schema(
                type="NUMBER",
                description="The first number (or the number to root/power, for 'root').",
            ),
            "b": types.Schema(
                type="NUMBER",
                description="The second number (or the root degree, for 'root').",
            ),
        },
        required=["operation", "a", "b"],
    ),
)

# A Tool bundles one or more FunctionDeclarations together. This is what
# gets passed into llm.generate(tools=...).
calculator_tool = types.Tool(function_declarations=[calculator_declaration])


# ---------------------------------------------------------------------------
# Server-side / built-in tool: Google Search grounding
#
# IMPORTANT: Unlike calculator_tool above, this tool has NO Python function
# behind it. There is nothing for our code to execute and no result for us
# to compute — Gemini performs the web search itself, on Google's servers,
# and returns an already-finished, grounded answer along with citation
# metadata. Our code only ever declares that this capability is available;
# it never "runs" google_search_tool the way it runs calculator().
# ---------------------------------------------------------------------------

google_search_tool = types.Tool(
    google_search=types.GoogleSearch()
)
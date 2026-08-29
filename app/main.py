"""
main.py

Command-line interface for the AI Research Agent.

This file is only responsible for interacting with the user in the
terminal: showing a welcome message, reading input, printing output,
and knowing when to stop. It contains no agent decision-making logic —
that all lives in agent.py, which this file simply calls into.

One ResearchAgent instance is created for the whole session, so it can
remember earlier messages as the conversation continues. Creating a new
instance per message would reset memory every time.
"""

from app.agent import ResearchAgent

EXIT_COMMANDS = {"exit", "quit"}


def main():
    """Run the command-line chat loop until the user exits."""
    print("=" * 50)
    print("AI Research Agent")
    print("Type your question below.")
    print("Type 'exit' or 'quit' to stop.")
    print("=" * 50)

    # Created once, outside the loop, so it remembers the conversation
    # across multiple messages in this session.
    agent = ResearchAgent()

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            # Handles Ctrl+D / Ctrl+C gracefully instead of a stack trace.
            print("\nGoodbye!")
            break

        # Handle empty input gracefully — just re-prompt.
        if not user_input:
            print("Please type a question, or 'exit' to quit.")
            continue

        if user_input.lower() in EXIT_COMMANDS:
            print("Goodbye!")
            break

        try:
            response = agent.run(user_input)
        except Exception as error:
            # TEMPORARY DEBUG VERSION — prints the real exception so we can
            # diagnose issues. Revert to a generic message before this goes
            # near a shared or public environment.
            print(f"Agent error: {error}")
            continue

        print(f"Agent: {response}")


if __name__ == "__main__":
    main()
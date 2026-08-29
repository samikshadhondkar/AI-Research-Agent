# 🤖 AI Research Agent

A beginner-friendly AI agent built from scratch using **Python and Google Gemini** to understand the core concepts behind AI agents without using frameworks like LangChain.

## What It Can Do

- 💬 Answer natural-language questions using Gemini
- 🧮 Use a custom **calculator tool** for arithmetic, powers, and roots
- 🌐 Use **Google Search grounding** for current information
- 🧠 Maintain **short-term conversation memory** during a session
- 🔧 Manually handle **LLM → tool call → tool result → LLM** workflows
- ⚠️ Handle API errors such as quota exhaustion

## How It Works

```text
User
 ↓
Gemini
 ↓
Does it need a tool?
 ├── No → Final Answer
 └── Yes
      ↓
   Execute Tool
      ↓
   Tool Result
      ↓
   Gemini
      ↓
   Final Answer

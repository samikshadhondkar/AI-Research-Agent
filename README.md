# 🤖 AI Research Agent

A beginner-friendly AI agent built with **Python** to understand the fundamentals of AI agents, LLMs, and tool calling.

The agent can analyze a user's request, decide whether a tool is required, execute the appropriate tool, and use the result to generate a final response.

## 🧠 How It Works

```text
User
 ↓
LLM
 ↓
Decide whether a tool is needed
 ↓
 ┌───────────────┐
 │               │
No Tool        Tool Needed
 │               │
 ↓               ↓
Answer       Execute Tool
                 ↓
            Tool Result
                 ↓
                LLM
                 ↓
              Answer
```

## ✨ Features

* LLM-powered responses
* Tool calling
* Calculator tool
* Basic agent loop
* Environment variable-based API key management
* Error handling
* Beginner-friendly architecture

## 🛠️ Tech Stack

* **Python**
* **LLM API**
* **Function / Tool Calling**
* **Git & GitHub**

## 📁 Project Structure

```text
ai-research-agent/
│
├── app/
│   ├── agent.py
│   ├── tools.py
│   ├── llm.py
│   └── main.py
│
├── tests/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## 🚀 Getting Started

Clone the repository:

```bash
git clone https://github.com/YOUR-USERNAME/ai-research-agent.git
cd ai-research-agent
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file and add your API key:

```text
LLM_API_KEY=your_api_key_here
```

Run the agent:

```bash
python app/main.py
```

## 💡 Example

```text
You: What is 238 × 47?

Agent: I'll use the calculator tool.

Tool Result: 11186

Agent: 238 × 47 = 11186.
```

## 📚 Learning Goals

This project is helping me understand:

* AI Agent Architecture
* LLMs
* Tool Calling
* Agent Loops
* API Integration
* Prompt Engineering
* Python
* Testing

## 🗺️ Roadmap

* [x] Basic LLM integration
* [x] First tool
* [x] Basic agent loop
* [ ] Web search
* [ ] RAG
* [ ] Memory
* [ ] Agent evaluation
* [ ] LangGraph
* [ ] MCP

## 👨‍💻 Author

**Sam**

Engineering Student | AI/ML | Software Development

> Building this project from the ground up to understand how AI agents actually work.

# 🤖 AI Research Agent

A beginner-friendly AI agent built from scratch using **Python** and **Google Gemini**.

The goal of this project is to understand how AI agents actually work internally — including LLM interaction, tool calling, conversation memory, and web search — without relying on frameworks such as LangChain.

---

## 📌 About the Project

This project is a simple AI research assistant that can:

- Understand natural-language questions
- Generate answers using Google Gemini
- Perform mathematical calculations using a custom Python tool
- Search the web using Google Search grounding
- Remember previous messages during a session
- Decide when a tool is required
- Handle API errors such as quota exhaustion gracefully

The agent is intentionally built with a **manual agent loop** so that the underlying concepts are easier to understand.

---

## 🧠 What is an AI Agent?

A basic chatbot follows this pattern:

```text
User → LLM → Response

# Project 6 — ReAct Agent

## What This Project Is

A ReAct (Reasoning + Acting) agent that answers questions by thinking through what to do, calling tools, observing results, and repeating that loop until it has a complete answer.

Unlike a plain LLM that can only answer from memory, or a RAG system that can only search a fixed knowledge base, a ReAct agent actively decides which tool to use, calls it with the right input, reads the result, and keeps going until the question is fully resolved.

---

## The Problem It Solves

A plain LLM with no tools attached is frozen at its training cutoff. It can't look things up, do live math, check the weather, or take any action in the world. It can only generate text based on patterns it saw during training.

A ReAct agent solves this by giving the LLM a set of tools and letting it decide how to use them. The LLM reasons about the problem, picks a tool, reads the result, and reasons again — looping until it has a complete answer.

---

## The ReAct Loop

Every question runs through this cycle:

````
Thought     →  The LLM reasons about what it needs
Action      →  It calls a specific tool with specific input
Observation →  It reads the tool's output
Thought     →  It reasons about whether it has enough to answer
...repeat as needed...
Answer      →  Final response grounded in real tool results
````

This loop is what makes the agent different from every previous project. Nothing in Projects 0–5 could decide mid-run to go get more information.

---

## Tools Available to the Agent

| Tool | What It Does |
|---|---|
| `calculator` | Evaluates math expressions |
| `wikipedia` | Fetches a summary for any topic |
| `weather` | Returns current conditions for a city |
| `dictionary` | Defines any word |

---

## Architecture

````mermaid
flowchart TD
    A[User Question] --> B[ReAct Agent]
    B --> C{Thought: what do I need?}
    C --> D[Action: call a tool]
    D --> E[Tool Executes]
    E --> F[Observation: read result]
    F --> G{Thought: do I have enough?}
    G -- No --> D
    G -- Yes --> H[Final Answer]
````

---

## Project Structure

````
project6_react_agent/
├── config.py       # Settings, API keys, model name, tool registry config
├── dataset.py      # Test questions and expected answers for evaluation
├── features.py     # Tool implementations — the actual callable functions
├── train.py        # Builds the tool registry and constructs the system prompt
├── evaluate.py     # Benchmarks agent vs plain LLM on the test question set
├── predict.py      # Runs the full ReAct loop for a single question
├── app.py          # Flask API — exposes the agent via HTTP endpoints
└── docs/
    ├── project_intro.md     ← this file
    ├── project_summary.md   ← added at completion
    └── concept_reference.md ← added at completion
````

---

## Key Concepts Introduced

- **ReAct pattern** — interleaving reasoning and acting in a loop
- **Tool use** — giving an LLM callable functions and letting it decide when to use them
- **Agent loop** — the Thought → Action → Observation cycle
- **Tool registry** — a dictionary mapping tool names to their implementations
- **Prompt engineering for agents** — structuring the system prompt so the LLM produces parseable Thought/Action/Observation output
- **Grounded answers** — responses built from real tool results rather than LLM memory

---

## Stack

- **Python 3.12.9**
- **Groq API** (Llama 3.1) — the LLM powering the agent's reasoning
- **Flask** — HTTP API wrapper
- **Wikipedia API** — `wikipedia` Python library
- **Open-Meteo API** — free weather API, no key required
- **Flask port**: 5003
````
````

Create your `docs/` folder inside `project7_react_agent/` and save this as `project_intro.md`. Once that's done, we'll move on to `config.py`.
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

## What the Agent Actually Is

The word "agent" can be misleading — it sounds like a single thing. It's actually a system of components working together. Here's exactly what comprises the Backyard Bird ReAct Agent:

### 1. The LLM — the brain
`llama-3.1-8b-instant` running on Groq's API. This is the component that reads the conversation and decides what to do next — which tool to call, what input to pass, and when it has enough information to give a final answer. The LLM has no awareness that it's inside a loop. It just receives a block of text and writes a response in the format we instructed.

### 2. The prompt — the job description
The system prompt in `config.py` is what turns a general-purpose LLM into a bird watching assistant that uses tools. Without it, the LLM would just answer from memory like any chatbot. The prompt tells it who it is, what tools it has, exactly how to format its output, and what rules to follow. The quality of the agent is directly tied to the quality of the prompt.

### 3. The tools — the hands
The four Python functions in `features.py` — calculator, wikipedia, weather, dictionary. The LLM cannot call these directly. It only writes text describing which tool it wants to use. Our code reads that text and calls the actual function.

### 4. The tool registry — the switchboard
The `TOOL_REGISTRY` dictionary in `features.py` maps tool name strings to their Python functions. When the agent loop sees `Action: weather` in the LLM's output, it looks up `"weather"` in the registry and calls `get_weather()`. This is the bridge between the LLM's text world and real Python code.

### 5. The parser — the interpreter
`parse_llm_output()` in `predict.py` reads the LLM's raw text response and extracts the structured fields — Thought, Action, Action Input, and Final Answer — using pattern matching. If the LLM drifts from the required format, the parser fails and the loop stops.

### 6. The ReAct loop — the conductor
`run_agent()` in `predict.py` is what makes this an agent rather than a single API call. It manages the conversation history, calls the LLM, passes output to the parser, calls the right tool, feeds the result back, and repeats until a Final Answer is produced or MAX_ITERATIONS is hit. None of the other components know about the loop — it orchestrates all of them.

### 7. The message history — the memory
A Python list of messages that grows with each iteration. Every LLM call receives the entire history so the model can see its previous reasoning and all tool results. This is the agent's only form of memory — it exists only for the duration of one question and resets completely for the next.

---

### The key insight

The LLM and the agent are not the same thing. The LLM is one component — the reasoning engine. The agent is the system built around it. Swapping to a larger, more capable LLM would improve answer quality without changing a single line of code in the agent itself, because the structure and the intelligence are separate concerns.

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
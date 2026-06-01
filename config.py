# config.py — Central settings for the Backyard Bird ReAct Agent
# All configuration lives here so every other script imports from one place
# Analogy: this is the control panel of the project — one place to change any setting

import os  # lets us read environment variables like API keys

# ── LLM settings ──────────────────────────────────────────────────────────────

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")  # reads your Groq key from the environment
MODEL_NAME = "llama-3.1-8b-instant"                 # the Groq model powering the agent's reasoning
MAX_TOKENS = 1024                                    # maximum tokens the LLM can generate per call
TEMPERATURE = 0.0                                    # 0.0 = deterministic, no randomness; best for agents

# ── Agent settings ─────────────────────────────────────────────────────────────

MAX_ITERATIONS = 6        # maximum number of Thought→Action→Observation cycles before giving up
AGENT_NAME = "Birdie"     # the agent's name, used in the system prompt

# ── Flask settings ─────────────────────────────────────────────────────────────

FLASK_PORT = 5003         # port the API runs on (5000=AirPlay, 5001=project1, 5002=project4)
FLASK_DEBUG = False       # debug mode off in production

# ── Weather settings ───────────────────────────────────────────────────────────

WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"  # free weather API, no key required
GEOCODING_API_URL = "https://geocoding-api.open-meteo.com/api/v1/search"  # converts city names to lat/lon

# ── Tool registry ──────────────────────────────────────────────────────────────
# This is a list of tool descriptions the LLM reads to know what tools exist
# The LLM never sees the actual Python functions — only these descriptions
# Analogy: this is the menu at a restaurant — the LLM reads the menu and orders, the kitchen (features.py) cooks

TOOLS = [
    {
        "name": "calculator",                                         # the name the LLM uses to call this tool
        "description": "Evaluates a math expression and returns the numeric result. Use this for any arithmetic, percentages, or unit conversions related to birds (e.g. weight ratios, flock sizes, migration distances).",
        "input_format": "a valid Python math expression as a string, e.g. '77 * 0.14' or '(3200 / 365)'"
    },
    {
        "name": "wikipedia",                                          # fetches a Wikipedia summary
        "description": "Fetches a Wikipedia summary for a bird species or ornithology topic. Use this for species facts, habitat, behavior, diet, range, and conservation status.",
        "input_format": "the name of a bird species or ornithology term, e.g. 'American Robin' or 'bird migration'"
    },
    {
        "name": "weather",                                            # looks up live weather
        "description": "Returns current weather conditions for a given city. Use this to advise whether conditions are good for bird watching, or to answer questions about weather in a bird's habitat.",
        "input_format": "a city name as a string, e.g. 'Hartford, CT' or 'Philadelphia, PA'"
    },
    {
        "name": "dictionary",                                         # defines ornithology vocabulary
        "description": "Defines an ornithology or bird-related term. Use this when the question involves technical vocabulary like 'precocial', 'altricial', 'passerine', or 'brood parasite'.",
        "input_format": "a single word or short phrase, e.g. 'precocial' or 'altricial'"
    },
]

# ── System prompt ──────────────────────────────────────────────────────────────
# This is the instruction given to the LLM at the start of every conversation
# It tells the LLM who it is, what tools it has, and exactly how to format its output
# Analogy: this is the job description handed to a new employee on their first day

TOOL_NAMES = [t["name"] for t in TOOLS]  # extracts just the names: ['calculator', 'wikipedia', 'weather', 'dictionary']
TOOL_DESCRIPTIONS = "\n".join(          # formats the tools into a readable block for the prompt
    f"- {t['name']}: {t['description']} Input format: {t['input_format']}"
    for t in TOOLS
)

SYSTEM_PROMPT = f"""You are {AGENT_NAME}, an expert backyard bird watching assistant for the northeastern United States.
You answer questions about bird species, behavior, identification, migration, and bird watching conditions.

You have access to these tools:
{TOOL_DESCRIPTIONS}

Each of your responses must contain EXACTLY ONE of the following — nothing more:

EITHER a tool call in this format:
Thought: <your reasoning>
Action: <tool_name>
Action Input: <tool_input>

OR a final answer in this format:
Thought: <your reasoning>
Final Answer: <your complete answer>

STRICT RULES:
- Output ONLY one block per response — never combine a tool call and a Final Answer in the same response
- Never write Action and Final Answer in the same response
- You MUST call the tool and wait for the Observation before writing Final Answer
- Never answer from memory — always use a tool to verify facts
- Once a tool returns a clear result, your very next response must be Final Answer
- When reporting weather, always include the temperature, conditions, and wind speed in your Final Answer — not just a yes or no- Do not search for extra information beyond what the question asks for
- Only answer questions about birds and bird watching
- For calculator questions involving multiple steps, show the full expression in one Action Input rather than multiple calls
- When reporting a percentage difference, always show the calculation: ((larger - smaller) / smaller) * 100
"""
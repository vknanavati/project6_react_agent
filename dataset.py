# dataset.py — Test questions and expected answers for the Backyard Bird ReAct Agent
# Used by evaluate.py to benchmark the agent against a plain LLM with no tools
# Analogy: a standardized exam — a fixed set of questions with known correct answers
# so we can measure whether having tools actually improves the agent's responses

# ── Test questions ─────────────────────────────────────────────────────────────
# Each entry is a dict with:
#   "question"      — what the user asks
#   "requires_tool" — which tool is needed to answer it correctly
#   "topic"         — the bird or concept being tested

TEST_QUESTIONS = [
    {
        "question": "What family of birds does the American Robin belong to and what is its scientific name?",
        "requires_tool": "wikipedia",                                        # answered in first sentence of article
        "topic": "American Robin",
    },
    {
        "question": "What does the term 'altricial' mean in ornithology?",
        "requires_tool": "dictionary",
        "topic": "ornithology vocabulary",
    },
    {
        "question": "A Northern Cardinal weighs about 45 grams. A Blue Jay weighs about 85 grams. How much heavier is the Blue Jay as a percentage of the Cardinal's weight? Use the formula: ((85 - 45) / 45) * 100",
        "requires_tool": "calculator",
        "topic": "bird weight comparison",
    },
    {
        "question": "Is it good weather for bird watching in Hartford, CT today?",
        "requires_tool": "weather",
        "topic": "bird watching conditions",
    },
    {
        "question": "What order of birds do Dark-eyed Juncos belong to and where are they found?",
        "requires_tool": "wikipedia",                                        # answered early in article
        "topic": "Dark-eyed Junco",
    },
    {
        "question": "What does 'irruption' mean in the context of bird watching?",
        "requires_tool": "dictionary",
        "topic": "ornithology vocabulary",
    },
    {
        "question": "A bird feeder holds 56 ounces of seed. A chickadee eats 0.1 ounces per day. Divide 56 by 0.1 to find how many days the feeder will last.",
        "requires_tool": "calculator",
        "topic": "feeder math",
    },
    {
        "question": "What is the Cedar Waxwing and what family does it belong to?",
        "requires_tool": "wikipedia",                                        # answered in first sentence
        "topic": "Cedar Waxwing",
    },
    {
        "question": "What is the difference between a passerine and a raptor?",
        "requires_tool": "dictionary",
        "topic": "ornithology vocabulary",
    },
    {
        "question": "Is it currently a good day to go birding in Philadelphia, PA?",
        "requires_tool": "weather",
        "topic": "bird watching conditions",
    },
]

# ── Plain LLM baseline prompt ──────────────────────────────────────────────────
# When evaluating, we ask the plain LLM the same questions with NO tools
# This lets us measure: does having tools actually produce better answers?
# Analogy: comparing an open-book exam score to a closed-book exam score
# for the same student on the same questions

BASELINE_SYSTEM_PROMPT = """You are a helpful bird watching assistant for the northeastern United States.
Answer questions about birds as accurately as you can using only your training knowledge.
You do not have access to any tools, live data, or the internet."""
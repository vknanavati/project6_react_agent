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
        "question": "What is the average wingspan of an American Robin?",   # factual species question
        "requires_tool": "wikipedia",                                        # needs a live lookup
        "topic": "American Robin",
    },
    {
        "question": "What does the term 'altricial' mean in ornithology?",  # vocabulary question
        "requires_tool": "dictionary",                                       # needs the glossary
        "topic": "ornithology vocabulary",
    },
    {
        "question": "A Northern Cardinal weighs about 45 grams. A Blue Jay weighs about 85 grams. How much heavier is the Blue Jay as a percentage of the Cardinal's weight?",
        "requires_tool": "calculator",                                       # needs arithmetic
        "topic": "bird weight comparison",
    },
    {
        "question": "Is it good weather for bird watching in Hartford, CT today?",  # live weather question
        "requires_tool": "weather",                                                  # needs real conditions
        "topic": "bird watching conditions",
    },
    {
        "question": "What do Dark-eyed Juncos eat?",                        # diet question
        "requires_tool": "wikipedia",                                        # needs a live lookup
        "topic": "Dark-eyed Junco",
    },
    {
        "question": "What does 'irruption' mean in the context of bird watching?",  # vocabulary question
        "requires_tool": "dictionary",                                               # needs the glossary
        "topic": "ornithology vocabulary",
    },
    {
        "question": "A bird feeder holds 3.5 pounds of seed. A chickadee eats about 0.1 ounces per day. There are 16 ounces in a pound. How many days will the feeder last if only chickadees use it?",
        "requires_tool": "calculator",                                       # multi-step arithmetic
        "topic": "feeder math",
    },
    {
        "question": "Where do Cedar Waxwings nest and what do they feed their chicks?",  # species behavior question
        "requires_tool": "wikipedia",                                                     # needs a live lookup
        "topic": "Cedar Waxwing",
    },
    {
        "question": "What is the difference between a passerine and a raptor?",  # two vocabulary terms
        "requires_tool": "dictionary",                                            # needs the glossary
        "topic": "ornithology vocabulary",
    },
    {
        "question": "Is it currently a good day to go birding in Philadelphia, PA?",  # live weather question
        "requires_tool": "weather",                                                    # needs real conditions
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
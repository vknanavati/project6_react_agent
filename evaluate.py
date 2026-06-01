# evaluate.py — Benchmarks the ReAct agent against a plain LLM with no tools
# Runs every question in dataset.py through both systems and compares the results
# Analogy: a side-by-side taste test — same questions, two different systems,
# so we can see clearly what tools add to the quality of answers

import json                        # for pretty-printing results
from groq import Groq              # the Groq client for calling the plain LLM baseline
import config                      # imports settings and the baseline system prompt
import dataset                     # imports the test questions
import predict                     # imports the run_agent function from predict.py

# ── Initialize the Groq client ─────────────────────────────────────────────────

client = Groq(api_key=config.GROQ_API_KEY)  # creates the Groq client using our API key

# ── Plain LLM baseline ─────────────────────────────────────────────────────────

def run_baseline(question: str) -> str:
    """
    Asks the plain LLM the question with no tools available.

    Plain explanation: sends the question directly to the LLM with a simple
    system prompt and no tool registry — just raw LLM memory.
    Analogy: the closed-book version of the exam — same questions, but the
    student can only use what they already know, no looking anything up.
    """
    response = client.chat.completions.create(       # calls the Groq API directly
        model=config.MODEL_NAME,                     # same model as the agent uses
        messages=[
            {"role": "system", "content": dataset.BASELINE_SYSTEM_PROMPT},  # no tools in this prompt
            {"role": "user", "content": question},   # the same question the agent gets
        ],
        max_tokens=config.MAX_TOKENS,                # same token limit
        temperature=config.TEMPERATURE,              # same temperature
    )
    return response.choices[0].message.content       # returns the plain LLM's answer

# ── Tool usage checker ─────────────────────────────────────────────────────────

def check_tool_usage(result: dict, required_tool: str) -> bool:
    """
    Checks whether the agent called the required tool for a given question.

    Plain explanation: looks at which tools the agent actually used and checks
    whether the expected tool appears in that list.
    Analogy: checking a student's work — did they use the right method to
    solve the problem, or did they just guess the answer?
    """
    tools_used = result.get("tools_used", [])        # gets the list of tools the agent called
    return required_tool in tools_used               # returns True if the required tool was used

# ── Single question evaluator ──────────────────────────────────────────────────

def evaluate_question(q: dict, index: int) -> dict:
    """
    Runs one question through both the agent and the baseline and returns a comparison.

    Plain explanation: takes one test question, gets answers from both systems,
    checks tool usage, and packages everything into a result dict.
    Analogy: one row in a comparison spreadsheet — question, agent answer,
    baseline answer, and a pass/fail for tool usage.
    """
    question = q["question"]                         # the question text
    required_tool = q["requires_tool"]               # the tool that should be called
    topic = q["topic"]                               # the bird topic being tested

    print(f"\n{'═' * 60}")
    print(f"Question {index + 1}/{len(dataset.TEST_QUESTIONS)}: {question}")
    print(f"Topic: {topic} | Required tool: {required_tool}")
    print(f"{'─' * 60}")

    # run the agent with full tool access
    print("🤖 Running agent...")
    agent_result = predict.run_agent(question, verbose=False)  # verbose=False keeps output clean
    agent_answer = agent_result["final_answer"]               # extracts the final answer
    tool_correct = check_tool_usage(agent_result, required_tool)  # checks tool usage
    tools_used = agent_result["tools_used"]                   # which tools were actually called
    iterations = agent_result["iterations"]                   # how many loop cycles it took

    # run the plain LLM baseline with no tools
    print("📚 Running baseline...")
    baseline_answer = run_baseline(question)                  # gets the plain LLM answer

    # print the comparison
    tool_status = "✅" if tool_correct else "❌"              # emoji for pass/fail
    print(f"\n{tool_status} Tool usage: expected '{required_tool}', used {tools_used}")
    print(f"🔄 Iterations: {iterations}")
    print(f"\n🤖 Agent answer:\n{agent_answer}")
    print(f"\n📚 Baseline answer:\n{baseline_answer[:300]}{'...' if len(baseline_answer) > 300 else ''}")

    return {                                                   # returns structured result
        "question": question,
        "topic": topic,
        "required_tool": required_tool,
        "tool_correct": tool_correct,
        "tools_used": tools_used,
        "iterations": iterations,
        "agent_answer": agent_answer,
        "baseline_answer": baseline_answer,
    }

# ── Summary printer ────────────────────────────────────────────────────────────

def print_summary(results: list):
    """
    Prints a summary table of all evaluation results.

    Plain explanation: counts how many questions the agent used the right tool
    for, and prints a clean table showing every question's outcome.
    Analogy: the final report card — one row per question, overall score at the bottom.
    """
    total = len(results)                                       # total number of questions
    tool_correct_count = sum(1 for r in results if r["tool_correct"])  # how many used the right tool
    avg_iterations = sum(r["iterations"] for r in results) / total     # average loop cycles

    print(f"\n{'═' * 60}")
    print("📊 EVALUATION SUMMARY")
    print(f"{'═' * 60}")
    print(f"{'Question':<45} {'Tool ✓':<8} {'Iters':<6}")
    print(f"{'─' * 60}")

    for r in results:                                          # prints one row per question
        short_q = r["question"][:42] + "..." if len(r["question"]) > 42 else r["question"]
        tool_mark = "✅" if r["tool_correct"] else "❌"       # pass/fail mark
        print(f"{short_q:<45} {tool_mark:<8} {r['iterations']:<6}")

    print(f"{'─' * 60}")
    print(f"Tool usage accuracy: {tool_correct_count}/{total} ({100 * tool_correct_count // total}%)")
    print(f"Average iterations per question: {avg_iterations:.1f}")
    print(f"{'═' * 60}\n")

# ── Main ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n🐦 Backyard Bird ReAct Agent — Evaluation")
    print(f"Model: {config.MODEL_NAME}")
    print(f"Test questions: {len(dataset.TEST_QUESTIONS)}")
    print(f"Max iterations per question: {config.MAX_ITERATIONS}")

    results = []                                               # stores all results

    for i, q in enumerate(dataset.TEST_QUESTIONS):            # loops through every test question
        result = evaluate_question(q, i)                      # evaluates one question
        results.append(result)                                 # adds to results list

    print_summary(results)                                     # prints the final summary table
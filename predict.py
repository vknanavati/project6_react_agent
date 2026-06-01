# predict.py — The ReAct agent loop for the Backyard Bird Assistant
# This is the heart of the project — it runs the Thought→Action→Observation cycle
# until the LLM produces a Final Answer
# Analogy: a detective who keeps investigating — gathering clues (tool results),
# reasoning about them, and only closing the case when they have a complete answer

import re                          # for parsing the LLM's output with pattern matching
from groq import Groq              # the Groq client for calling the LLM
import config                      # imports settings, system prompt, and tool definitions
import features                    # imports the tool registry

# ── Initialize the Groq client ─────────────────────────────────────────────────

client = Groq(api_key=config.GROQ_API_KEY)  # creates the Groq client using our API key from config

# ── Output parser ──────────────────────────────────────────────────────────────

def parse_llm_output(text: str) -> dict:
    """
    Parses the LLM's raw text output into structured fields.

    Plain explanation: reads the LLM's response and extracts the Thought,
    Action, Action Input, and Final Answer fields using pattern matching.
    Analogy: a form processor — the LLM fills out a structured form in plain
    text, and this function reads each field off the form.
    """
    result = {                                               # initializes empty result dict
        "thought": None,                                     # the LLM's reasoning
        "action": None,                                      # the tool name to call
        "action_input": None,                                # the input to pass to the tool
        "final_answer": None,                                # the final answer if loop is done
    }

    # extract Thought field
    thought_match = re.search(r"Thought:\s*(.+?)(?=Action:|Final Answer:|$)", text, re.DOTALL)
    if thought_match:                                        # if a Thought field was found
        result["thought"] = thought_match.group(1).strip()  # extracts and cleans the thought text

    # extract Action field
    action_match = re.search(r"Action:\s*(.+?)(?=Action Input:|$)", text, re.DOTALL)
    if action_match:                                         # if an Action field was found
        result["action"] = action_match.group(1).strip()    # extracts and cleans the tool name

    # extract Action Input field
    input_match = re.search(r"Action Input:\s*(.+?)(?=Thought:|Observation:|$)", text, re.DOTALL)
    if input_match:                                          # if an Action Input field was found
        result["action_input"] = input_match.group(1).strip()  # extracts and cleans the tool input

    # extract Final Answer field
    answer_match = re.search(r"Final Answer:\s*(.+?)$", text, re.DOTALL)
    if answer_match:                                         # if a Final Answer field was found
        result["final_answer"] = answer_match.group(1).strip()  # extracts and cleans the final answer

    return result                                            # returns the structured dict

# ── Tool caller ────────────────────────────────────────────────────────────────

def call_tool(tool_name: str, tool_input: str) -> str:
    """
    Looks up a tool in the registry and calls it with the given input.

    Plain explanation: takes the tool name and input parsed from the LLM's output,
    finds the matching Python function, and runs it.
    Analogy: the switchboard operator — receives a call for 'weather', connects
    it to the get_weather function, and returns the result.
    """
    tool_name = tool_name.lower().strip()                    # normalizes the tool name to lowercase

    if tool_name not in features.TOOL_REGISTRY:              # checks if the tool exists
        available = ", ".join(features.TOOL_REGISTRY.keys()) # lists available tool names
        return f"Unknown tool '{tool_name}'. Available tools: {available}"

    func = features.TOOL_REGISTRY[tool_name]                 # looks up the function in the registry
    return func(tool_input)                                  # calls the function and returns the result

# ── ReAct loop ─────────────────────────────────────────────────────────────────

def run_agent(question: str, verbose: bool = True) -> dict:
    """
    Runs the full ReAct loop for a given question.

    Plain explanation: sends the question to the LLM, reads its response,
    calls tools as needed, feeds results back, and repeats until the LLM
    produces a Final Answer or the maximum number of iterations is reached.
    Analogy: a detective investigation — the detective (LLM) reads the case file
    (question), requests evidence (tool calls), studies each piece of evidence
    (observations), and only files a report (Final Answer) when the case is solved.
    """

    # build the initial message history with the system prompt and user question
    messages = [
        {"role": "system", "content": config.SYSTEM_PROMPT},  # the agent's instructions
        {"role": "user", "content": question},                  # the user's question
    ]

    steps = []                                               # tracks every step of the loop for logging
    final_answer = None                                      # will hold the final answer when found
    tools_used = []                                          # tracks which tools were called

    if verbose:
        print(f"\n🐦 Question: {question}")
        print("─" * 60)

    for iteration in range(config.MAX_ITERATIONS):           # loops up to MAX_ITERATIONS times

        # ── Step 1: call the LLM ───────────────────────────────────────────────
        response = client.chat.completions.create(           # sends the message history to Groq
            model=config.MODEL_NAME,                         # the model specified in config
            messages=messages,                               # full conversation history
            max_tokens=config.MAX_TOKENS,                    # maximum response length
            temperature=config.TEMPERATURE,                  # 0.0 = deterministic output
        )
        llm_output = response.choices[0].message.content    # extracts the LLM's text response

        if verbose:
            print(f"\n[Iteration {iteration + 1}] LLM Output:")
            print(llm_output)

        # ── Step 2: parse the LLM's output ────────────────────────────────────
        parsed = parse_llm_output(llm_output)               # extracts Thought/Action/Answer fields

        # ── Step 3: check for Final Answer ────────────────────────────────────
        if parsed["final_answer"]:                           # if the LLM produced a final answer
            final_answer = parsed["final_answer"]            # store it
            steps.append({                                   # log this step
                "iteration": iteration + 1,
                "thought": parsed["thought"],
                "final_answer": final_answer,
            })
            if verbose:
                print(f"\n✅ Final Answer: {final_answer}")
            break                                            # exit the loop — we're done

        # ── Step 4: call the requested tool ───────────────────────────────────
        if parsed["action"] and parsed["action_input"]:      # if the LLM requested a tool call
            tool_name = parsed["action"]                     # the tool to call
            tool_input = parsed["action_input"]              # the input to pass
            tools_used.append(tool_name)                     # track which tools were used

            if verbose:
                print(f"\n🔧 Calling tool: {tool_name}({tool_input!r})")

            observation = call_tool(tool_name, tool_input)  # calls the tool and gets the result

            if verbose:
                print(f"📋 Observation: {observation[:200]}{'...' if len(observation) > 200 else ''}")

            # ── Step 5: add the exchange to message history ────────────────────
            # we add the LLM's output and the tool result to the conversation
            # so the LLM has full context on its next iteration
            messages.append({"role": "assistant", "content": llm_output})      # LLM's reasoning
            # truncate long observations before adding to history to avoid hitting token limits
            truncated = observation[:500] if len(observation) > 500 else observation  # keeps history manageable
            messages.append({"role": "user", "content": f"Observation: {truncated}"})  # tool result

            steps.append({                                   # log this step
                "iteration": iteration + 1,
                "thought": parsed["thought"],
                "action": tool_name,
                "action_input": tool_input,
                "observation": observation,
            })

        else:
            # LLM didn't produce a valid action or final answer — something went wrong
            if verbose:
                print("\n⚠️  Could not parse a valid Action or Final Answer. Stopping.")
            break                                            # exit the loop to avoid infinite spinning

    # if we hit MAX_ITERATIONS without a final answer, return what we have
    if not final_answer:                                     # checks if we ever got a final answer
        final_answer = "I was unable to reach a final answer within the allowed number of steps."

    return {                                                 # returns a structured result dict
        "question": question,                                # the original question
        "final_answer": final_answer,                        # the agent's answer
        "steps": steps,                                      # the full reasoning trace
        "tools_used": tools_used,                            # list of tools that were called
        "iterations": len(steps),                            # total number of loop cycles
    }

# ── Main ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # test the agent with a few bird questions
    test_questions = [
        "What do American Robins eat?",
        "Is it good weather for bird watching in Hartford, CT today?",
        "What does the term altricial mean?",
        "A chickadee weighs 11 grams and a blue jay weighs 85 grams. How many times heavier is the blue jay?",
    ]

    for question in test_questions:                          # loops through each test question
        result = run_agent(question, verbose=True)           # runs the full ReAct loop
        print("\n" + "═" * 60 + "\n")                       # prints a separator between questions
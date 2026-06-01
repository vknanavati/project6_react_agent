# train.py — Builds the tool registry and validates all tools before the agent runs
# In previous projects this script trained a model from scratch
# Here the LLM is already trained — this script instead verifies our pipeline is working
# Analogy: a pre-flight checklist — the pilot didn't build the plane, but still checks
# every instrument before takeoff to make sure nothing is broken

import json          # for pretty-printing the tool registry as readable output
import config        # imports settings, tool definitions, and the system prompt
import features      # imports the actual tool functions and TOOL_REGISTRY

# ── Display the tool registry ──────────────────────────────────────────────────

def show_tool_registry():
    """
    Prints the tool registry so you can confirm all tools are registered correctly.

    Plain explanation: loops through every tool in the registry and prints its name
    and the function it maps to.
    Analogy: reading the staff roster before a shift — confirming every role
    is filled before the restaurant opens.
    """
    print("\n── Tool Registry ──────────────────────────────────────────────")
    for name, func in features.TOOL_REGISTRY.items():   # loops through each tool name and its function
        print(f"  {name:12} → {func.__name__}()")       # prints the mapping in a readable format
    print()

# ── Display the system prompt ──────────────────────────────────────────────────

def show_system_prompt():
    """
    Prints the full system prompt so you can confirm the LLM's instructions are correct.

    Plain explanation: prints the exact text that gets sent to the LLM at the
    start of every conversation.
    Analogy: reading the employee handbook out loud before the first day —
    confirming the instructions are complete and make sense.
    """
    print("── System Prompt ───────────────────────────────────────────────")
    print(config.SYSTEM_PROMPT)                          # prints the full system prompt from config.py
    print()

# ── Smoke test each tool ───────────────────────────────────────────────────────

def smoke_test_tools():
    """
    Calls each tool with a simple input and checks it returns a non-empty response.

    Plain explanation: runs a quick test of every tool to make sure none of them
    crash or return empty results before the agent tries to use them for real.
    Analogy: a sound check before a concert — the band plays a few notes through
    each microphone to confirm everything is connected and working.
    """
    print("── Smoke Tests ─────────────────────────────────────────────────")

    # define one simple test input per tool
    tests = [
        ("calculator", "45 + 85"),                      # simple addition
        ("wikipedia", "American Robin"),                 # well-known bird species
        ("weather", "Hartford, CT"),                     # a city from our test questions
        ("dictionary", "passerine"),                     # a term in our glossary
    ]

    all_passed = True                                    # tracks whether all tests pass

    for tool_name, test_input in tests:                  # loops through each test case
        print(f"  Testing '{tool_name}' with input: '{test_input}'")
        try:
            func = features.TOOL_REGISTRY[tool_name]    # looks up the function in the registry
            result = func(test_input)                    # calls the function with the test input
            if result and len(result) > 0:               # checks the result is non-empty
                # prints just the first 80 characters so output stays readable
                print(f"  ✅ PASSED — {result[:80]}{'...' if len(result) > 80 else ''}")
            else:
                print(f"  ❌ FAILED — empty response")  # flags an empty result as a failure
                all_passed = False                       # marks overall test as failed
        except Exception as e:                           # catches any crash during the tool call
            print(f"  ❌ FAILED — {str(e)}")            # prints the error message
            all_passed = False                           # marks overall test as failed
        print()

    return all_passed                                    # returns True if all tests passed

# ── Summary ────────────────────────────────────────────────────────────────────

def print_summary(all_passed: bool):
    """
    Prints a final summary of the smoke test results.

    Plain explanation: tells you clearly whether the pipeline is ready to use.
    Analogy: the final thumbs up or thumbs down from the flight crew before takeoff.
    """
    print("── Summary ─────────────────────────────────────────────────────")
    if all_passed:
        print("  ✅ All tools passed. The agent pipeline is ready.")
        print(f"  Model : {config.MODEL_NAME}")
        print(f"  Tools : {', '.join(features.TOOL_REGISTRY.keys())}")
        print(f"  Port  : {config.FLASK_PORT}")
    else:
        print("  ❌ One or more tools failed. Fix the errors above before running the agent.")
    print()

# ── Main ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n🐦 Backyard Bird ReAct Agent — Pipeline Validation\n")
    show_tool_registry()                                 # prints the tool registry
    show_system_prompt()                                 # prints the system prompt
    all_passed = smoke_test_tools()                      # runs the smoke tests
    print_summary(all_passed)                            # prints the final summary
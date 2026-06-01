# app.py — Flask API for the Backyard Bird ReAct Agent
# Exposes the agent via HTTP endpoints so it can be called from any application
# Analogy: a receptionist desk — it receives incoming requests, routes them to
# the agent, and sends the response back in a clean, structured format

from flask import Flask, request, jsonify  # Flask for the web server, request for reading input, jsonify for JSON responses
import config                              # imports settings including the Flask port
import predict
import threading                              # allows Flask to run in a background thread                             # imports the run_agent function

# ── Initialize Flask ───────────────────────────────────────────────────────────

app = Flask(__name__)                      # creates the Flask application instance

# ── Health check endpoint ──────────────────────────────────────────────────────

@app.route("/health", methods=["GET"])
def health():
    """
    Returns the status of the API and agent configuration.

    Plain explanation: a simple endpoint that confirms the API is running
    and shows the current model and tool configuration.
    Analogy: knocking on the door to check if anyone is home before
    sending a full request.
    """
    return jsonify({                                         # returns a JSON response
        "status": "ok",                                      # confirms the API is running
        "agent": config.AGENT_NAME,                          # the agent's name
        "model": config.MODEL_NAME,                          # the LLM being used
        "tools": list(predict.features.TOOL_REGISTRY.keys()),  # available tools
        "max_iterations": config.MAX_ITERATIONS,             # max ReAct loop cycles
    })

# ── Ask endpoint ───────────────────────────────────────────────────────────────

@app.route("/ask", methods=["POST"])
def ask():
    """
    Runs the full ReAct agent loop for a bird-related question.

    Plain explanation: accepts a question in the request body, passes it
    to the agent, and returns the final answer along with the full
    reasoning trace showing every tool call the agent made.
    Analogy: submitting a question to an expert and getting back not just
    the answer but their complete notes showing how they reached it.
    """
    data = request.get_json()                                # parses the JSON request body

    if not data or "question" not in data:                   # validates the request has a question
        return jsonify({"error": "Request body must include a 'question' field"}), 400

    question = data["question"]                              # extracts the question string

    if not question.strip():                                 # checks the question is not empty
        return jsonify({"error": "Question cannot be empty"}), 400

    result = predict.run_agent(question, verbose=False)      # runs the ReAct loop silently

    return jsonify({                                         # returns structured JSON response
        "question": result["question"],                      # the original question
        "answer": result["final_answer"],                    # the agent's final answer
        "tools_used": result["tools_used"],                  # which tools were called
        "iterations": result["iterations"],                  # how many loop cycles it took
        "steps": result["steps"],                            # the full reasoning trace
    })

# ── Tools endpoint ─────────────────────────────────────────────────────────────

@app.route("/tools", methods=["GET"])
def tools():
    """
    Returns the list of available tools and their descriptions.

    Plain explanation: lists every tool the agent can use, along with
    a description of what it does and what input format it expects.
    Analogy: the menu at a restaurant — shows what's available before
    you place an order.
    """
    return jsonify({                                         # returns JSON list of tools
        "tools": config.TOOLS                               # the full tool definitions from config
    })

# ── Main ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"\n🐦 {config.AGENT_NAME} — Backyard Bird Assistant")
    print(f"   Model   : {config.MODEL_NAME}")
    print(f"   Tools   : {', '.join(predict.features.TOOL_REGISTRY.keys())}")
    print(f"   API     : http://127.0.0.1:{config.FLASK_PORT}")
    print(f"   Ask me anything about birds and bird watching.")
    print(f"   Type 'quit' to exit.\n")

    # start Flask in a background thread so it doesn't block the interactive prompt
    flask_thread = threading.Thread(                         # creates a background thread for Flask
        target=lambda: app.run(                              # runs the Flask server in the thread
            host="0.0.0.0",
            port=config.FLASK_PORT,
            debug=False,                                     # debug must be False when using threads
            use_reloader=False                               # reloader must be off when using threads
        )
    )
    flask_thread.daemon = True                               # thread dies when main program exits
    flask_thread.start()                                     # starts the Flask thread in the background

    # interactive prompt runs in the main thread
    while True:                                              # keeps the prompt running until user quits
        question = input("Ask a question: ").strip()         # displays the prompt and waits for input

        if not question:                                     # skips empty input
            continue

        if question.lower() == "quit":                       # exits if user types quit
            print("\nHappy birding! 🐦\n")
            break

        result = predict.run_agent(question, verbose=True)   # runs the ReAct loop
        print("\n" + "═" * 60 + "\n")                       # prints a separator between questions
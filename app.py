"""
Web wrapper for Gemini Function Calling demonstration.
Exposes the CLI functionality via HTTP endpoints for deployment on Render.
"""
from flask import Flask, request, jsonify
from gemini_client import GeminiFunctionCallingClient
import os
import sys

app = Flask(__name__)

# Initialize the Gemini client
try:
    client = GeminiFunctionCallingClient()
    client.start_chat()
except Exception as e:
    print(f"Error initializing Gemini client: {e}", file=sys.stderr)
    client = None


@app.route('/', methods=['GET'])
def health():
    """Health check endpoint."""
    if client is None:
        return jsonify({
            "status": "error",
            "message": "Gemini client not initialized. Check GEMINI_API_KEY environment variable."
        }), 500
    
    return jsonify({
        "status": "ok",
        "message": "Gemini Function Calling API is running",
        "endpoints": {
            "/": "Health check (GET)",
            "/chat": "Send a message to Gemini (POST)",
            "/chat/new": "Start a new chat session (POST)",
            "/history": "Get conversation history (GET)"
        }
    })


@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat requests via HTTP."""
    if client is None:
        return jsonify({
            "error": "Gemini client not initialized. Check GEMINI_API_KEY environment variable."
        }), 500
    
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"error": "Missing 'message' field in request body"}), 400
        
        user_message = data['message']
        verbose = data.get('verbose', False)
        
        # Send message to Gemini
        flow_info = client.send_message(user_message, verbose=verbose)
        client.conversation_history.append(flow_info)
        
        return jsonify({
            "response": flow_info['final_response'],
            "function_calls": flow_info['function_calls'],
            "api_responses": flow_info['api_responses']
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/chat/new', methods=['POST'])
def new_chat():
    """Start a new chat session."""
    if client is None:
        return jsonify({
            "error": "Gemini client not initialized. Check GEMINI_API_KEY environment variable."
        }), 500
    
    try:
        client.start_chat()
        return jsonify({
            "message": "New chat session started",
            "conversation_history_cleared": True
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/history', methods=['GET'])
def get_history():
    """Get conversation history."""
    if client is None:
        return jsonify({
            "error": "Gemini client not initialized. Check GEMINI_API_KEY environment variable."
        }), 500
    
    try:
        return jsonify({
            "conversation_history": client.conversation_history,
            "summary": client.get_conversation_summary()
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)


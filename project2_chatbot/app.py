"""
AI-Powered Chatbot — Flask Application
Cloud Computing Task 4
Deployed on AWS EC2 with S3 for chat log storage.
"""

from flask import Flask, render_template, request, jsonify
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
from chatbot_engine import ChatBot
from cloud_config import CloudConfig

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'chatbot-dev-key')

bot = ChatBot()
cloud = CloudConfig()

# In-memory chat sessions
sessions = {}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/chat/stream', methods=['GET'])
def api_chat_stream():
    """Process user message and return streaming bot response via SSE."""
    message = request.args.get('message', '').strip()
    session_id = request.args.get('session_id', str(uuid.uuid4()))

    if not message:
        return jsonify({'error': 'Message required.'}), 400

    def generate():
        import json
        full_response = ""
        # Get bot response stream
        for chunk_text in bot.get_response_stream(message, session_id=session_id):
            full_response += chunk_text
            # Send chunk to client
            yield f"data: {json.dumps({'chunk': chunk_text})}\n\n"
        
        # Store in session after completion
        if session_id not in sessions:
            sessions[session_id] = []
        
        time_str = datetime.now().strftime('%H:%M')
        # We don't save the user message until the stream ends to keep them together
        sessions[session_id].append({'role': 'user', 'text': message, 'time': time_str})
        sessions[session_id].append({
            'role': 'bot', 'text': full_response, 'time': time_str,
            'category': 'Generative AI', 'method': 'gemini'
        })
        
        # Send termination signal
        yield f"data: [DONE]\n\n"

    return app.response_class(generate(), mimetype='text/event-stream')


@app.route('/api/suggestions')
def api_suggestions():
    return jsonify({'suggestions': bot.get_suggestions()})


@app.route('/api/save-session', methods=['POST'])
def api_save_session():
    """Save chat session to AWS S3."""
    data = request.get_json()
    session_id = data.get('session_id', '')
    if session_id in sessions:
        result = cloud.save_chat_log(session_id, sessions[session_id])
        return jsonify(result)
    return jsonify({'status': 'error', 'message': 'Session not found.'})


@app.route('/api/cloud/status')
def api_cloud_status():
    return jsonify(cloud.get_status())


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5002))
    print(f"\n{'='*50}")
    print(f"  SmartBot — AI-Powered Chatbot")
    print(f"  Running on http://localhost:{port}")
    print(f"  Cloud Storage: {'AWS S3' if cloud.is_connected() else 'LOCAL'}")
    print(f"  Model: Google Gemini 1.5 Flash")
    print(f"{'='*50}\n")
    app.run(host='0.0.0.0', port=port, debug=True)

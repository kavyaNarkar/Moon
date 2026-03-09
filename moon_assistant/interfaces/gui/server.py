import os
import webbrowser
from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
from ...core.brain import query_llm
from ...core.parser import parse_command, quick_parse
from ...core.executor import execute_task, get_response_text, perform_action
from ...utils.logger import logger

app = Flask(__name__)
CORS(app)

# Path to static files
STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')

@app.route('/')
def index():
    return send_from_directory(STATIC_DIR, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(STATIC_DIR, path)

@app.route('/api/command', methods=['POST'])
def handle_command():
    from ...interfaces.voice_output import speak
    data = request.json
    user_input = data.get('command', '').strip()
    muted = data.get('mute', False)
    
    if not user_input:
        return jsonify({'response': 'No command received.'})
    
    logger.info(f"GUI Command: {user_input} (Muted: {muted})")
    
    # 1. Try Fast Track (Keywords)
    command = quick_parse(user_input)
    
    if not command:
        # 2. Fallback to LLM
        llm_response = query_llm(user_input)
        command = parse_command(llm_response, original_text=user_input)
    
    # 3. Get response text and speak IMMEDIATELY
    response_text = get_response_text(command)
    if not muted:
        speak(response_text)
    
    # 4. Perform Action (Parallel/Sequential as needed)
    action_result = perform_action(command)
    final_response = action_result if action_result and isinstance(action_result, str) else response_text
    
    return jsonify({'response': final_response})

@app.route('/api/wake_word', methods=['POST'])
def handle_wake_word():
    """
    Blocks until the wake word is detected.
    """
    from ...interfaces.wake_word import wait_for_moon
    logger.info("GUI Waiting for wake word...")
    
    if wait_for_moon():
        return jsonify({'status': 'detected'})
    return jsonify({'status': 'error'})

@app.route('/api/voice', methods=['POST'])
def handle_voice():
    """
    Triggers voice listening and processing.
    """
    from ...interfaces.voice_input import listen_for_command
    from ...interfaces.voice_output import speak
    
    data = request.json or {}
    muted = data.get('mute', False)
    
    # 1. Listen for voice
    logger.info(f"GUI Voice listening triggered (Muted: {muted})")
    text_command = listen_for_command()
    
    if not text_command:
        return jsonify({'response': 'I didn\'t catch that.', 'user_text': ''})
        
    # 2. Process Command
    logger.info(f"GUI Voice Command: {text_command}")
    
    command = quick_parse(text_command)
    if not command:
        llm_response = query_llm(text_command)
        command = parse_command(llm_response, original_text=text_command)
        
    # 3. Get response text and speak IMMEDIATELY
    response_text = get_response_text(command)
    if not muted:
        speak(response_text)
        
    # 4. Perform Action
    action_result = perform_action(command)
    final_response = action_result if action_result and isinstance(action_result, str) else response_text
    
    return jsonify({
        'response': final_response,
        'user_text': text_command
    })

@app.route('/api/security/verify', methods=['POST'])
def verify_security():
    """Handles security verification (Fingerprint simulation or Password)."""
    data = request.json
    mode = data.get('mode', 'fingerprint')
    password = data.get('password', '')
    
    from ...core.security_manager import security_manager
    
    if mode == 'password':
        success, user_or_message = security_manager.verify_password(password)
        if success:
            return jsonify({'status': 'unlocked', 'user': user_or_message})
        else:
            return jsonify({'status': 'locked', 'message': user_or_message})
    else:
        # Simulate fingerprint detection
        success, message = security_manager.verify_fingerprint()
        if success:
            return jsonify({'status': 'unlocked', 'user': 'Kavya'})
        else:
            return jsonify({'status': 'locked', 'message': message})

@app.route('/api/security/add_face', methods=['POST'])
def add_security_face():
    # Deprecated for face, kept as stub if needed for other biometric management
    return jsonify({'status': 'error', 'message': 'Endpoint deprecated.'})

def start_gui():
    from .app import start_desktop_app
    start_desktop_app()

if __name__ == '__main__':
    start_gui()

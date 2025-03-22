from flask import Flask, request, jsonify
from flask_cors import CORS
import hashlib
import os
from face_auth import capture_and_match_face
from voice_auth import recognize_voice
from digitpin import validate_pin
import logging
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configure logging with more detail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s - [%(filename)s:%(lineno)d]'
)

# Set maximum upload size (16MB)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Environment variables for authentication
AUTH_PIN_DIGIT = os.getenv("AUTH_PIN_DIGIT", "7648")
AUTH_PIN_DIGIT_HASH = hashlib.sha256(AUTH_PIN_DIGIT.encode()).hexdigest()
AUTH_PIN_VOICE = os.getenv("AUTH_PIN_VOICE", "HELLO")
REFERENCE_IMAGE_PATH = os.getenv("REFERENCE_IMAGE_PATH", r"C:\Users\mahes\OneDrive\Pictures\Camera Roll\CHECK4.jpg")

# Validate reference image path
if not os.path.exists(REFERENCE_IMAGE_PATH):
    logging.error(f"Reference image not found at {REFERENCE_IMAGE_PATH}. Please update REFERENCE_IMAGE_PATH.")
else:
    logging.info(f"Reference image loaded from {REFERENCE_IMAGE_PATH}")

@app.route('/')
def test():
    return "Backend is running on http://127.0.0.1:5000!"

@app.route('/validate-pin', methods=['POST'])
def validate_pin_api():
    if request.content_type != 'application/json':
        logging.error("Invalid content type: %s", request.content_type)
        return jsonify({"success": False, "message": "Invalid content type"}), 415

    data = request.get_json(silent=True)
    logging.info("Received PIN validation request with data: %s", data)
    if not data or "pin" not in data:
        logging.error("Missing or invalid JSON: %s", data)
        return jsonify({"success": False, "message": "PIN is required"}), 400

    user_entered_pin = str(data["pin"]).strip()
    if not user_entered_pin:
        logging.error("PIN is empty")
        return jsonify({"success": False, "message": "PIN cannot be empty"}), 400

    if validate_pin(user_entered_pin, AUTH_PIN_DIGIT_HASH):
        logging.info("PIN authentication successful")
        return jsonify({"success": True, "message": "PIN verified"}), 200
    logging.warning("PIN authentication failed")
    return jsonify({"success": False, "message": "Incorrect PIN"}), 401

@app.route('/face-auth', methods=['POST'])
def face_auth_api():
    if request.content_type != 'application/json':
        logging.error("Invalid content type: %s", request.content_type)
        return jsonify({"success": False, "message": "Invalid content type"}), 415

    data = request.get_json(silent=True)
    logging.info("Received face auth request")
    if not data or "image" not in data:
        logging.error("Missing or invalid JSON: %s", data)
        return jsonify({"success": False, "message": "Image data is required"}), 400

    base64_image = data["image"]
    logging.info(f"Base64 image (first 50 chars): {base64_image[:50]}...")
    if not isinstance(base64_image, str) or not base64_image.startswith('data:image'):
        logging.error("Invalid image format")
        return jsonify({"success": False, "message": "Invalid image format"}), 400

    result = capture_and_match_face(REFERENCE_IMAGE_PATH, base64_image)
    logging.info(f"Face verification result: {result}")
    if result:
        logging.info("Face authentication successful")
        return jsonify({"success": True, "message": "Face verified"}), 200
    logging.warning("Face verification failed")
    return jsonify({"success": False, "message": "Face verification failed"}), 401

@app.route('/voice-auth', methods=['POST'])
def voice_auth_api():
    """
    Voice authentication endpoint that uses live microphone input to capture and verify the user's voice.
    This endpoint does not require an audio file upload since the voice is captured directly on the server.
    """
    logging.info("Received voice auth request")

    try:
        # Call the recognize_voice function with the expected voice PIN
        success, message = recognize_voice(AUTH_PIN_VOICE, max_attempts=3)
        logging.info(f"Voice recognition result: success={success}, message='{message}'")

        if success:
            logging.info("Voice authentication successful")
            return jsonify({"success": True, "message": "Voice verified"}), 200
        logging.warning(f"Voice authentication failed: {message}")
        return jsonify({"success": False, "message": message}), 401
    except Exception as e:
        logging.error(f"Voice auth endpoint error: {type(e).__name__}: {str(e)}")
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500

if __name__ == '__main__':
    logging.info("🚀 Starting Flask Server...")
    app.run(host="127.0.0.1", port=5000, debug=True)
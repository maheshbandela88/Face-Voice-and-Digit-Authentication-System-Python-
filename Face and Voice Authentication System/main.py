# main.py
import os
import logging
import signal
import sys
import hashlib
from face_auth import capture_and_match_face
from voice_auth import recognize_voice  # Corrected import

# Custom handler to force UTF-8 encoding
class UTF8StreamHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            msg = self.format(record)
            stream = self.stream
            stream.write(msg + self.terminator)
            self.flush()
        except UnicodeEncodeError:
            msg = msg.encode("ascii", errors="replace").decode("ascii")
            stream.write(msg + self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)

# Configure logging with the custom handler
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[UTF8StreamHandler(sys.stdout)]
)

# Graceful exit for Ctrl+C
def signal_handler(sig, frame):
    logging.info("Exiting gracefully...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Configuration (hardcoded or set via environment variables)
REFERENCE_IMAGE_PATH = r"C:\Users\mahes\OneDrive\Pictures\Camera Roll\check.jpg" # Reference image path in main.py
AUTH_PIN = os.getenv("AUTH_PIN", "HELLO")  # Default PIN
AUTH_PIN_HASH = hashlib.sha256(AUTH_PIN.encode()).hexdigest()  # Hash the PIN for security
MAX_VOICE_ATTEMPTS = int(os.getenv("MAX_VOICE_ATTEMPTS", 3))  # Default attempts

# Perform face and voice authentication
if capture_and_match_face(REFERENCE_IMAGE_PATH):
    if recognize_voice(AUTH_PIN_HASH, MAX_VOICE_ATTEMPTS):
        logging.info("Authentication Successful")
    else:
        logging.error("Voice Authentication Failed")
else:
    logging.error("Face Authentication Failed")

# Cleanup captured face image
if os.path.exists("captured_face.jpg"):
    os.remove("captured_face.jpg")
    logging.info("🗑️ Cleaned up captured image.")

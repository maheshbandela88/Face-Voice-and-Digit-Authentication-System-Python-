import cv2
import face_recognition
import logging
import base64
import numpy as np
import os
from io import BytesIO
from PIL import Image

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s - [%(filename)s:%(lineno)d]'
)

# Set face match threshold (lowered to 0.5 for better matching, adjustable via env)
FACE_MATCH_THRESHOLD = float(os.getenv("FACE_MATCH_THRESHOLD", 0.5))

def decode_base64_image(base64_image: str) -> np.ndarray:
    """Decodes a base64 image string into an OpenCV image."""
    try:
        if not base64_image.startswith('data:image'):
            raise ValueError("Invalid base64 image format")

        parts = base64_image.split(',')
        if len(parts) != 2:
            raise ValueError("Malformed base64 image string")

        img_data = base64.b64decode(parts[1])
        if len(img_data) > 10 * 1024 * 1024:  # Limit to 10MB
            raise ValueError("Image size exceeds limit")

        nparr = np.frombuffer(img_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            raise ValueError("Failed to decode image")

        # Save for debugging
        cv2.imwrite("debug_captured.jpg", image)
        logging.info("Captured image saved as debug_captured.jpg for inspection")

        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    except Exception as e:
        logging.error(f"Error decoding base64 image: {e}")
        return None

def get_face_encoding(image: np.ndarray) -> np.ndarray:
    """Extracts the face encoding from an image."""
    try:
        encodings = face_recognition.face_encodings(image)
        logging.info(f"Number of faces detected: {len(encodings)}")

        if not encodings:
            logging.warning("No face detected in image")
            return None
        if len(encodings) > 1:
            logging.warning("Multiple faces detected; using first detected face")

        return encodings[0]
    except Exception as e:
        logging.error(f"Error extracting face encoding: {e}")
        return None

def load_and_encode_image(image_path: str) -> np.ndarray:
    """Loads an image from file and extracts its face encoding."""
    if not os.path.exists(image_path):
        logging.error(f"Image file not found: {image_path}")
        return None
    try:
        image = face_recognition.load_image_file(image_path)
        if image is None or image.shape[0] == 0:
            logging.error("Failed to load image properly")
            return None
        return get_face_encoding(image)
    except Exception as e:
        logging.error(f"Error loading image {image_path}: {e}")
        return None

def capture_and_match_face(ref_image_path: str, base64_image: str) -> bool:
    """Compares a reference face image with a base64-encoded captured image."""
    logging.info("Starting face verification process...")

    # Load and encode reference image
    ref_encoding = load_and_encode_image(ref_image_path)
    if ref_encoding is None:
        logging.error("Reference image encoding failed")
        return False

    # Decode and encode captured image
    captured_image = decode_base64_image(base64_image)
    if captured_image is None:
        logging.error("Captured image decoding failed")
        return False

    captured_encoding = get_face_encoding(captured_image)
    if captured_encoding is None:
        logging.error("Captured face encoding failed")
        return False

    # Compare faces
    match = face_recognition.compare_faces([ref_encoding], captured_encoding, tolerance=FACE_MATCH_THRESHOLD)[0]
    distance = face_recognition.face_distance([ref_encoding], captured_encoding)[0]
    logging.info(f"Face distance: {distance} (threshold: {FACE_MATCH_THRESHOLD})")

    if match:
        logging.info("✅ Face verification successful!")
    else:
        logging.warning("❌ Face verification failed!")

    return match

if __name__ == "__main__":
    ref_path = r"C:\Users\mahes\OneDrive\Pictures\Camera Roll\CHECK4.jpg"
    test_base64 = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD..."
    result = capture_and_match_face(ref_path, test_base64)
    print("Match result:", result)
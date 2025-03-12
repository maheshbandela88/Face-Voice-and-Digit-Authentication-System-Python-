import face_recognition  # The actual library
from face_auth import capture_and_match_face  # Your script
from voice_recognition import recognize_voice
# Load a sample image and learn how to recognize it
known_image = face_recognition.load_image_file(r"C:\Users\mahes\OneDrive\Pictures\Camera Roll\check.jpg")
known_encoding = face_recognition.face_encodings(known_image)[0]

# Predefined voice authentication PIN
AUTH_PIN = "HEY HOW ARE YOU"

# Perform face and voice authentication
if capture_and_match_face(known_encoding):
    print("Face Matched. Now verifying voice...")
    recognize_voice(AUTH_PIN)
else:
    print("Face Not Recognized: Access Denied")

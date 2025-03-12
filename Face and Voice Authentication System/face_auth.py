import cv2
import face_recognition
import logging
import os
import time
import sys
import threading

# Configuration (hardcoded or set via environment variables)
FACE_MATCH_THRESHOLD = float(os.getenv("FACE_MATCH_THRESHOLD", 0.6))  # Default threshold
MAX_FACE_ATTEMPTS = int(os.getenv("MAX_FACE_ATTEMPTS", 3))  # Default attempts

def capture_and_match_face(ref_image_path):
    """Captures an image from the webcam and checks if the face matches."""

    try:
        known_image = face_recognition.load_image_file(ref_image_path)
        known_image = cv2.cvtColor(known_image, cv2.COLOR_BGR2RGB)
        known_encodings = face_recognition.face_encodings(known_image)

        if not known_encodings:
            logging.error("⚠️ No face detected in the reference image. Try using a clearer image.")
            return False
        else:
            known_encoding = known_encodings[0]
            logging.info("✅ Reference face encoding generated successfully.")

    except Exception as e:
        logging.error(f"❌ Error loading reference image: {e}")
        return False

    video_capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not video_capture.isOpened():
        logging.error("❌ Error: Webcam not available.")
        return False

    face_attempts = 0

    while face_attempts < MAX_FACE_ATTEMPTS:
        time.sleep(0.5)

        for _ in range(5):
            ret, frame = video_capture.read()

        if not ret:
            logging.error("❌ Error: Could not capture image. Try again.")
            return False

        cv2.imwrite("captured_face.jpg", frame)
        logging.info(f"📸 Captured image saved as 'captured_face.jpg' (Attempt {face_attempts+1}/{MAX_FACE_ATTEMPTS})")

        video_capture.release()
        cv2.destroyAllWindows()

        try:
            captured_image = face_recognition.load_image_file("captured_face.jpg")
            captured_image = cv2.cvtColor(captured_image, cv2.COLOR_BGR2RGB)
            captured_encodings = face_recognition.face_encodings(captured_image)

            if not captured_encodings:
                logging.error("⚠️ No face detected. Move closer to the camera and ensure good lighting.")
                face_attempts += 1
                if face_attempts >= MAX_FACE_ATTEMPTS:
                    logging.error("❌ Maximum capture attempts reached. Exiting...")
                    return False
                logging.info(f"🔄 Retrying image capture... (Attempt {face_attempts+1}/{MAX_FACE_ATTEMPTS})")
                time.sleep(5)
                video_capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
                continue

            if len(captured_encodings) > 1:
                logging.error("⚠️ Multiple faces detected. Ensure only one person is in front of the camera.")
                face_attempts += 1
                if face_attempts >= MAX_FACE_ATTEMPTS:
                    logging.error("❌ Maximum capture attempts reached. Exiting...")
                    return False
                logging.info(f"🔄 Retrying image capture... (Attempt {face_attempts+1}/{MAX_FACE_ATTEMPTS})")
                time.sleep(5)
                video_capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
                continue

        except Exception as e:
            logging.error(f"❌ Error processing captured image: {e}")
            face_attempts += 1
            if face_attempts >= MAX_FACE_ATTEMPTS:
                logging.error("❌ Maximum capture attempts reached. Exiting...")
                return False
            logging.info(f"🔄 Retrying image capture... (Attempt {face_attempts+1}/{MAX_FACE_ATTEMPTS})")
            time.sleep(5)
            video_capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            continue

        face_distance = face_recognition.face_distance([known_encoding], captured_encodings[0])[0]
        match = face_recognition.compare_faces([known_encoding], captured_encodings[0], tolerance=FACE_MATCH_THRESHOLD)[0]

        if match and face_distance < FACE_MATCH_THRESHOLD:
            logging.info("✅ Face authentication successful. Proceeding to voice authentication...")
            return True
        else:
            logging.error("❌ Face authentication failed. Retrying in 5 seconds.")
            face_attempts += 1
            if face_attempts >= MAX_FACE_ATTEMPTS:
                logging.error("❌ Maximum capture attempts reached. Exiting...")
                return False
            time.sleep(5)
            video_capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            continue

    return False

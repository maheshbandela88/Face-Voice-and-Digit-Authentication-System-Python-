import cv2
import face_recognition
import numpy as np

def capture_and_match_face(known_encoding):
    video_capture = cv2.VideoCapture(0)
    ret, frame = video_capture.read()
    video_capture.release()
    
    if not ret:
        print("Error: Could not capture image.")
        return False
    
    # Save the captured frame
    cv2.imwrite("captured_face.jpg", frame)
    captured_image = face_recognition.load_image_file("captured_face.jpg")
    captured_encoding = face_recognition.face_encodings(captured_image)
    
    if len(captured_encoding) == 0:
        print("Error: No face detected.")
        return False
    
    match = face_recognition.compare_faces([known_encoding], captured_encoding[0])[0]
    if match:
        print("Face lock successfully completed. Let's go to step 2: Voice lock.")
    return match

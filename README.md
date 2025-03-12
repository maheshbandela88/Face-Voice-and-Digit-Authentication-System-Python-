Face and Voice Authentication System
This project implements a dual authentication system using face recognition and voice recognition to provide an extra layer of security. It ensures that only authorized individuals can gain access by first verifying their face and then validating their voice.

🔒 How It Works:
1.Face Recognition Step:

A predefined image of the authorized person is stored.
The system captures a live image from the webcam and compares it with the stored image.
If the face matches, the system proceeds to the next step.

2.Voice Authentication Step:

The user is asked to say a predefined authentication PIN (e.g., "HEY HOW ARE YOU").
The system records the user's voice and converts it into text.
If the spoken phrase matches the predefined PIN, access is granted.
✅ Features:
Real-time Face Recognition using OpenCV and face_recognition.
Live Voice Authentication with SpeechRecognition.
Multi-Factor Security by combining facial and voice verification.
Automated Access Decision: If both checks pass, access is granted; otherwise, access is denied.

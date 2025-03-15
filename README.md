Face, Voice, and Digit PIN Authentication System

This project implements a triple-layer authentication system using face recognition, voice recognition, and a numeric PIN to provide enhanced security. It ensures that only authorized individuals can gain access by verifying their face, validating their voice, and confirming their PIN.

🔒 How It Works:

1️⃣ Digit PIN Authentication Step:
1.The user is prompted to enter a predefined 4-digit PIN.
2.If the entered PIN matches the stored hash, the system proceeds to the next step.
2️⃣ Face Recognition Step:
1.A predefined image of the authorized person is stored.
2.The system captures a live image from the webcam and compares it with the stored image.
3.If the face matches, the system proceeds to the next step.

3️⃣ Voice Authentication Step:
1.The user is asked to say a predefined authentication phrase (e.g., "HEY HOW ARE YOU").
2.The system records the user's voice and converts it into text.
3.If the spoken phrase matches the predefined voice PIN, access is granted.

✅ Features:
✔ Multi-Factor Authentication: Combines Digit PIN, Facial Recognition, and Voice Authentication.
✔ Real-time Face Recognition: Uses OpenCV and face_recognition.
✔ Live Voice Authentication: Powered by SpeechRecognition.
✔ Digit PIN Security: Uses SHA-256 hashing to securely verify the numeric PIN.
✔ Automated Access Decision:

If all three checks pass, access is granted.
If any one fails, access is denied.

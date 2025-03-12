# voice_auth.py
import speech_recognition as sr
import logging
import os
import hashlib

def recognize_voice(auth_pin_hash, max_attempts):
    """Captures the user's voice and checks if it matches the predefined PIN."""
    recognizer = sr.Recognizer()

    # Get microphone index from environment, else auto-detect
    MIC_INDEX = os.getenv("MIC_INDEX")

    if MIC_INDEX is not None:
        try:
            MIC_INDEX = int(MIC_INDEX)
        except ValueError:
            MIC_INDEX = None  # Reset if not a valid number

    # List available microphones
    mic_list = sr.Microphone.list_microphone_names()

    # Auto-detect default microphone if index is invalid
    if MIC_INDEX is None or MIC_INDEX < 0 or MIC_INDEX >= len(mic_list):
        MIC_INDEX = None

    logging.info(f"🎤 Using microphone: {mic_list[MIC_INDEX] if MIC_INDEX is not None else 'Default'}")

    for attempt in range(max_attempts):
        with sr.Microphone(device_index=MIC_INDEX) as source:
            logging.info("🎤 Say the authentication PIN...")
            recognizer.adjust_for_ambient_noise(source)

            try:
                audio = recognizer.listen(source, timeout=5)
            except sr.WaitTimeoutError:
                logging.error("⏳ No speech detected. Try again.")
                continue
            except OSError as e:
                logging.error(f"🎤 Microphone Error: {e}")
                return False

        try:
            spoken_text = recognizer.recognize_google(audio).strip().upper()
            logging.info(f"🔊 You said: {spoken_text}")

            if hashlib.sha256(spoken_text.encode()).hexdigest() == auth_pin_hash:
                logging.info("✅ Voice authentication successful. Access Granted!")
                return True
            else:
                logging.error("❌ Incorrect voice PIN. Try again.")
        except sr.UnknownValueError:
            logging.error("🤷 Error: Could not understand audio.")
        except sr.RequestError:
            logging.error("⚠️ Error: Speech recognition service is unavailable.")

    logging.error("❌ Maximum attempts reached. Access Denied.")
    return False

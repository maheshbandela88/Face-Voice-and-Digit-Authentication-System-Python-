# voice_auth.py
import speech_recognition as sr
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s - [%(filename)s:%(lineno)d]'
)

def recognize_voice(auth_pin, max_attempts=3):
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
                return False, f"Microphone error: {str(e)}"

        try:
            spoken_text = recognizer.recognize_google(audio).strip().upper()
            logging.info(f"🔊 You said: '{spoken_text}'")

            if spoken_text == auth_pin.upper():
                logging.info("✅ Voice authentication successful. Access Granted!")
                return True, "Voice verified"
            else:
                logging.error("❌ Incorrect voice PIN. Try again.")
                remaining_attempts = max_attempts - (attempt + 1)
                return False, f"Incorrect voice PIN. {remaining_attempts} attempts remaining."
        except sr.UnknownValueError:
            logging.error("🤷 Error: Could not understand audio.")
            return False, "Could not understand audio"
        except sr.RequestError as e:
            logging.error(f"⚠️ Error: Speech recognition service is unavailable: {str(e)}")
            return False, f"Speech recognition service unavailable: {str(e)}"

    logging.error("❌ Maximum attempts reached. Access Denied.")
    return False, "Maximum attempts reached. Access Denied."

if __name__ == "__main__":
    # Test the function standalone
    result, msg = recognize_voice("HELLO", max_attempts=3)
    print(f"Result: {result}, Message: {msg}")
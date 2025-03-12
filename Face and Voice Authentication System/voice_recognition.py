import speech_recognition as sr

def recognize_voice(auth_pin):
    with sr.Microphone() as source:
        print("Say the authentication PIN...")
        recognizer = sr.Recognizer()
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        
        # Convert speech to text
        try:
            spoken_text = recognizer.recognize_google(audio).strip().upper()
            print(f"You said: {spoken_text}")
            
            if spoken_text == auth_pin:
                print("Voice lock successfully completed. Access Granted: PIN Unlocked.")
                return True
            else:
                print("Voice did not match. Access Denied.")
                return False
        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError:
            print("Speech recognition service error")
        
        return False

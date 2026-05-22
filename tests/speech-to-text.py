import speech_recognition as sr
import pyaudio
import sys

def test_microphone_indices():
    p = pyaudio.PyAudio()
    print("Searching for valid microphones...")
    valid_indices = []
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        if dev.get('maxInputChannels') > 0:
            print(f"Index {i}: {dev.get('name')}")
            valid_indices.append(i)
    p.terminate()
    return valid_indices

def run_stt():
    r = sr.Recognizer()
    indices = test_microphone_indices()
    
    if not indices:
        print("No input devices found at all.")
        return

    # Try default first, then others
    try:
        print("\nAttempting to use default microphone...")
        with sr.Microphone() as source:
            print("Default mic works!")
            process_audio(r, source)
            return
    except Exception as e:
        print(f"Default mic failed: {e}")

    for index in indices:
        try:
            print(f"\nAttempting to use device index {index}...")
            with sr.Microphone(device_index=index) as source:
                print(f"Success with index {index}!")
                process_audio(r, source)
                return
        except Exception as e:
            print(f"Index {index} failed: {e}")

def process_audio(recognizer, source):
    print("Adjusting for noise... (speak into mic)")
    recognizer.adjust_for_ambient_noise(source, duration=1)
    print("Listening...")
    try:
        audio = recognizer.listen(source, timeout=8, phrase_time_limit=5)
        print("Recognizing...")
        text = recognizer.recognize_google(audio)
        print(f"Result: {text}")
    except sr.WaitTimeoutError:
        print("No speech detected.")
    except sr.UnknownValueError:
        print("Could not understand audio.")
    except sr.RequestError as e:
        print(f"Service error: {e}")

if __name__ == "__main__":
    run_stt()
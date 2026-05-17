import speech_recognition as sr
import pyaudio
import os
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from utils.logger import logging as log

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
        log.warning("No input device found")
        return None

    # Try default first, then others
    try:
        print("\nAttempting to use default microphone...")
        with sr.Microphone() as source:
            print("Default mic works!")
            log.info("Mic is working")
            return process_audio(r, source)
    except Exception as e:
        print(f"Default mic failed: {e}")
        log.error(f"Default mic failed: {e}")

    for index in indices:
        try:
            print(f"\nAttempting to use device index {index}...")
            with sr.Microphone(device_index=index) as source:
                print(f"Success with index {index}!")
                return process_audio(r, source)
        except Exception as e:
            print(f"Index {index} failed: {e}")
            log.error(f"index {index} failed: {e}")
    return None

def process_audio(recognizer, source):
    print("Adjusting for noise... (speak into mic)")
    recognizer.adjust_for_ambient_noise(source, duration=1)
    print("Listening...")
    try:
        audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
        print("Recognizing...")
        text = recognizer.recognize_google(audio)
        print(f"Result: {text}")
        log.info(f"Audio successfully recognized as {text}")
        return text
    except sr.WaitTimeoutError:
        print("No speech detected.")
        log.error("No speech detected")
    except sr.UnknownValueError:
        print("Could not understand audio.")
        log.error("could not understand audio")
    except sr.RequestError as e:
        print(f"Service error: {e}")
        log.error(f"{e}")
    return None

if __name__ == "__main__":
    run_stt()
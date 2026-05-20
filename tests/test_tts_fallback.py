import os
import sys

# Add project root to sys.path to ensure absolute imports work correctly
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.tts import TTSEngine, check_wifi
import time

def test_tts_fallback():
    print("=== TTS Fallback Logic Test ===")
    
    # Prompt the user to enter a voice name
    print("\nAvailable voices: jessica, brian, mark, lily, gtts, pyttsx3")
    voice_input = input("Enter a voice name to test: ").strip().lower()

    # Determine method and name
    tts_method = "pyttsx3"
    voice_name = "jessica"

    if voice_input in ["jessica", "brian", "mark", "lily"]:
        tts_method = "elevenlabs"
        voice_name = voice_input.capitalize()
    elif voice_input == "gtts":
        tts_method = "gtts"
        voice_name = "gTTS"
    elif voice_input == "pyttsx3":
        tts_method = "pyttsx3"
        voice_name = "pyttsx3"
    else:
        print(f"Unknown voice '{voice_input}'. Defaulting to pyttsx3/Jessica.")
        tts_method = "pyttsx3"
        voice_name = "Jessica"

    # Display current WiFi status
    wifi_status = check_wifi()
    print(f"\nCurrent WiFi Status: {'Connected' if wifi_status else 'Disconnected'}")
    
    # Initialize Engine and test
    print(f"Requesting TTS with Method: {tts_method} | Voice Name: {voice_name}")
    engine = TTSEngine(default_method=tts_method, voice_name=voice_name)
    
    test_text = "This is a test of the text to speech fallback system."
    print(f"\nSpeaking: '{test_text}'")
    
    # Run the speak command
    engine.speak(test_text, method=tts_method, voice_name=voice_name)
    
    # Wait to let audio play
    time.sleep(3)
    
    print("\nTest completed. Please toggle your WiFi and run this test again to verify both states.")

if __name__ == "__main__":
    test_tts_fallback()

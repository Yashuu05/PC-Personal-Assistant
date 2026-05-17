"""
Speech-to-Speech Integration Module for Personal Assistant (LOQ).
Combines stt.py (Speech-to-Text) and tts.py (Text-to-Speech) into an
end-to-end voice loop designed to run asynchronously in a CustomTkinter application.
"""

import os
import sys
import threading
import re
from dotenv import load_dotenv

# Add project root to sys.path to ensure absolute imports work correctly
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from utils.logger import logging as log
from core.stt import run_stt
from core.tts import TTSEngine

def extract_name_and_greet(text):
    """
    Analyzes the user input text for name-introduction patterns.
    If a pattern matches, returns a custom greeting; otherwise returns a default echo.
    """
    if not text:
        return None
        
    text_lower = text.lower().strip()
    
    # Patterns to match: "my name is <name>", "i am <name>", "i'm <name>", "hello my name is <name>"
    patterns = [
        r"\bmy name is\s+([a-zA-Z\s]+)",
        r"\bi'm\s+([a-zA-Z\s]+)",
        r"\bi am\s+([a-zA-Z\s]+)",
        r"\bthis is\s+([a-zA-Z\s]+)"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            # Capture and clean the name
            name = match.group(1).strip().title()
            # Handle cases where they speak a full greeting with trailing characters
            name_words = name.split()
            if name_words:
                # Take the first word or name block
                first_name = name_words[0]
                return f"Nice to meet you, {first_name}!"
                
    # Fallback to general conversational echo
    return f"I heard you say: {text}"


class SpeechToSpeechSystem:
    """
    Manages the active speech interaction loop.
    Optimized to be imported directly by a CustomTkinter GUI and run in a separate thread.
    """
    def __init__(self, tts_method="pyttsx3", voice_name="Jessica"):
        # Initialize the underlying text-to-speech engine
        self.tts = TTSEngine(default_method=tts_method, voice_name=voice_name)
        log.info(f"SpeechToSpeechSystem initialized with TTS method: {tts_method}")

    def run_cycle(self, tts_method=None, voice_name=None):
        """
        Executes a single synchronous Speech-to-Speech loop:
        1. Listen via STT (Speech-to-Text).
        2. Process/parse the text to generate an appropriate response.
        3. Speak the response using the configured TTS method.
        
        Returns a tuple of (recognized_text, response_text).
        """
        log.info("Starting Speech-to-Speech cycle...")
        
        # Step 1: Run STT to capture microphone input
        user_input = run_stt()
        
        if not user_input:
            response = "Sorry, I didn't hear anything. Please try again."
            log.warning("Speech-to-Speech: No input detected.")
            # Speak fallback warning
            self.tts.speak(response, method=tts_method, voice_name=voice_name)
            return None, response
            
        # Step 2: Determine appropriate response (greetings parser or fallback echo)
        response = extract_name_and_greet(user_input)
        log.info(f"Speech-to-Speech interaction: [User: '{user_input}'] -> [Assistant: '{response}']")
        
        # Step 3: Speak the response
        self.tts.speak(response, method=tts_method, voice_name=voice_name)
        
        return user_input, response

    def run_cycle_async(self, callback=None, tts_method=None, voice_name=None):
        """
        Runs the Speech-to-Speech cycle in a background thread to prevent GUI lockup.
        
        Parameters:
            callback: An optional callback function that receives (user_text, assistant_response).
                      This is ideal for updating CustomTkinter UI labels and history.
            tts_method: Override default TTS method (e.g., 'elevenlabs', 'gtts', 'pyttsx3')
            voice_name: Override default assistant voice name
        """
        def thread_target():
            user_text, assistant_response = self.run_cycle(tts_method=tts_method, voice_name=voice_name)
            if callback:
                try:
                    callback(user_text, assistant_response)
                except Exception as e:
                    log.error(f"Error in Speech-to-Speech async callback: {e}")
                    
        # Start background daemon thread
        s2s_thread = threading.Thread(target=thread_target, daemon=True)
        s2s_thread.start()
        return s2s_thread

    def stop(self):
        """Instantly interrupts any ongoing speech playback."""
        self.tts.stop()


# Self-test code
if __name__ == "__main__":
    print("\n=== LOQ Speech-to-Speech End-to-End Test ===")
    print("This will listen to your voice and reply using TTS.")
    print("Example: Speak 'Hello, my name is John' to verify name-matching.")
    
    # Initialize the system
    system = SpeechToSpeechSystem(tts_method="pyttsx3")
    
    # Run the cycle synchronously
    user_text, assistant_response = system.run_cycle()
    
    print("\n--- Test Complete ---")
    print(f"Recognized Speech: {user_text}")
    print(f"Assistant Response: {assistant_response}")

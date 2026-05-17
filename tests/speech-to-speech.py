"""
Voice Command Execution Test Script (LOQ).
Runs an end-to-end voice-controlled test cycle with Speech-to-Text,
low-latency command mapping, asynchronous execution, and text-to-speech feedback.
Implements a robust 3-trial loop for speech recognition failures with intelligent fallbacks.
"""

import os
import sys
import time

# Add project root to sys.path to ensure absolute imports work correctly
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.speech_to_speech import SpeechToSpeechSystem
from core.stt import run_stt
from utils.logger import logging as log

def run_voice_command_test():
    # Initialize the SpeechToSpeechSystem
    # Defaulting to gtts which will automatically cascade fallback to offline pyttsx3 if unavailable
    system = SpeechToSpeechSystem(tts_method="gtts", voice_name="Jessica")
    
    print("\n=== LOQ Speech-to-Speech Command Execution Test ===")
    print("Workflow: You have 3 trials to speak a valid system command listed in commands.json.")
    print("Examples to speak: 'open notepad', 'open calculator', 'check ip address'.")
    
    # Step 1: Program prompts for voice input
    """
    greeting = "Please say a command, such as open notepad."
    print(f"\nLOQ: \"{greeting}\"")
    system.tts.speak(greeting, method="gtts")
    """
    trial = 0
    max_trials = 3
    
    while trial < max_trials:
        trial += 1
        print(f"\n--- [Trial {trial}/{max_trials}] Listening for voice command... ---")
        
        # Step 2 & 3: Run Speech Recognition to capture voice input
        raw_speech = run_stt()
        
        if not raw_speech:
            # Step 7: If speech is not recognized, prompt "Please repeat again"
            if trial < max_trials:
                repeat_prompt = "Please repeat again."
                print(f"LOQ: \"{repeat_prompt}\"")
                system.tts.speak(repeat_prompt, method="gtts")
            else:
                fail_prompt = "Unrecognizable command. Max trials reached. Exiting."
                print(f"LOQ: \"{fail_prompt}\"")
                system.tts.speak(fail_prompt, method="gtts")
                time.sleep(3.0)  # Let audio play before process exits
            continue
            
        print(f"Raw speech recognized: \"{raw_speech}\"")
        
        # Step 4 & 5: Clean and match command key
        cleaned_text = system.clean_input(raw_speech)
        print(f"Cleaned search text: \"{cleaned_text}\"")
        
        matched_key, shell_command = system.match_command(raw_speech)
        
        if matched_key:
            # Step 6: Command matched successfully!
            # Format a natural speaking response: e.g. "open notepad" -> "opening notepad"
            if matched_key.startswith("open "):
                spoken_subject = matched_key.replace("open ", "")
                tts_response = f"opening {spoken_subject}"
            else:
                tts_response = f"executing command {matched_key}"
                
            print(f"LOQ: \"{tts_response}\"")
            system.tts.speak(tts_response, method="gtts")
            
            # Execute command asynchronously
            # Setting skip_safety=True here for automated test execution flow
            system.execute_command(shell_command, matched_key, skip_safety=True)
            
            # CRITICAL: Keep process alive to allow asynchronous MCI playback to finish speaking!
            time.sleep(2.0)
            
            print("\n[SUCCESS] Command executed asynchronously. Test completed successfully.")
            return True
        else:
            # Speech captured but matched nothing (invalid command keyword)
            print(f"Invalid command key: No match found for '{cleaned_text}'.")
            if trial < max_trials:
                invalid_prompt = "Invalid command keyword. Please repeat again."
                print(f"LOQ: \"{invalid_prompt}\"")
                system.tts.speak(invalid_prompt, method="gtts")
            else:
                fail_prompt = "Invalid command. Max trials reached. Exiting."
                print(f"LOQ: \"{fail_prompt}\"")
                system.tts.speak(fail_prompt, method="gtts")
                time.sleep(3.0)  # Let audio play before process exits
                
    print("\n[FAILED] Test completed without executing any command.")
    return False

if __name__ == "__main__":
    try:
        run_voice_command_test()
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")

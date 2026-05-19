"""
Speech-to-Speech Integration Module for Personal Assistant (LOQ).
Combines STT (Speech-to-Text), TTS (Text-to-Speech), and high-performance
command execution matching into an end-to-end voice loop.
Designed to run asynchronously with full CustomTkinter support.
"""

import os
import sys
import threading
import re
import json
import subprocess
import time
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
    If a pattern matches, returns a custom greeting; otherwise returns None.
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
            name_words = name.split()
            if name_words:
                # Take the first name word
                first_name = name_words[0]
                return f"Nice to meet you, {first_name}!"
                
    return None


class SpeechToSpeechSystem:
    """
    Unified end-to-end voice assistant system.
    Handles Speech Recognition, Intent Matching (using low-latency Dict + Regex),
    asynchronous shell execution, and premium voice synthesis.
    """
    def __init__(self, tts_method="pyttsx3", voice_name="Jessica", commands_path=None):
        # 1. Initialize Text-to-Speech Engine
        self.tts = TTSEngine(default_method=tts_method, voice_name=voice_name)
        
        # 2. Setup system commands registry
        if not commands_path:
            commands_path = os.path.join(project_root, "config", "commands.json")
        self.commands_path = commands_path
        self.commands = {}
        self.command_regex = None
        self.critical_commands = ["shutdown", "restart", "sleep", "hibernate", "del", "delete"]
        
        self.load_commands()
        log.info("SpeechToSpeechSystem successfully initialized.")

    def load_commands(self):
        """Loads system command mappings from JSON and pre-compiles regex parser."""
        try:
            if not os.path.exists(self.commands_path):
                log.error(f"Commands config not found at: {self.commands_path}")
                return False
                
            with open(self.commands_path, "r") as f:
                self.commands = json.load(f)
                
            log.info(f"Loaded {len(self.commands)} system commands from config.")
            
            # Sort command keys by length descending to prioritize longer matches (e.g. "open powershell as admin" before "open powershell")
            sorted_keys = sorted(self.commands.keys(), key=len, reverse=True)
            
            # Create pre-compiled regular expression pattern
            pattern = r"\b(" + "|".join(re.escape(k) for k in sorted_keys) + r")\b"
            self.command_regex = re.compile(pattern, re.IGNORECASE)
            log.info("Successfully pre-compiled command matching regex pattern.")
            return True
        except Exception as e:
            log.error(f"Error loading system commands config: {e}")
            return False

    def clean_input(self, text):
        """
        Cleans user input by lowercasing, stripping punctuation,
        mapping synonyms, and filtering conversational filler words.
        This provides smart, natural match results with near-zero latency.
        """
        if not text:
            return ""
        text = text.lower().strip()
        
        # Remove common punctuation
        text = re.sub(r"[.,\/#!$%\^&\*;:{}=\-_`~()?]", "", text)
        
        # Synonym normalizations
        text = text.replace("shut down", "shutdown")
        text = text.replace("wi fi", "wifi")
        text = text.replace("wi-fi", "wifi")
        text = text.replace("signout", "sign out")
        
        # Filter out filler words
        filler_words = {"please", "could", "you", "can", "hey", "loq", "the", "a", "an", "now", "right", "want", "would", "like"}
        words = text.split()
        filtered_words = [w for w in words if w not in filler_words]
        
        cleaned = " ".join(filtered_words)
        return cleaned

    def match_command(self, user_input):
        """
        Performs high-performance command matching.
        1. Exact Hash-Map Check: O(1) time complexity.
        2. Pre-Compiled Regex Search: O(L) scan in C, matching substrings anywhere in the string.
        """
        cleaned = self.clean_input(user_input)
        if not cleaned:
            return None, None
            
        start_time = time.perf_counter()
        
        # O(1) Exact Match Check
        if cleaned in self.commands:
            latency = (time.perf_counter() - start_time) * 1_000_000
            log.info(f"O(1) Exact Match: '{cleaned}' found in {latency:.2f} μs.")
            return cleaned, self.commands[cleaned]
            
        # O(L) Regex Substring Match
        match = self.command_regex.search(cleaned)
        latency = (time.perf_counter() - start_time) * 1_000_000
        
        if match:
            matched_key = match.group(1).lower()
            shell_command = self.commands.get(matched_key)
            log.info(f"O(L) Regex Match: '{matched_key}' found in {latency:.2f} μs.")
            return matched_key, shell_command
            
        log.info(f"No command match found for: '{cleaned}' (Time: {latency:.2f} μs)")
        return None, None

    def is_critical(self, matched_key):
        """Checks if the command represents a critical system action requiring safety validation."""
        return any(keyword in matched_key for keyword in self.critical_commands)

    def execute_command(self, shell_command, matched_key, confirmation_callback=None, skip_safety=False):
        """
        Executes the shell command asynchronously.
        Supports GUI-friendly safety callback to show yes/no dialogs in CustomTkinter.
        """
        if not shell_command:
            return False
            
        if shell_command.startswith("py:"):
            success, _ = self.execute_python_command(shell_command)
            return success
            
        # Check critical system commands safety
        if self.is_critical(matched_key) and not skip_safety:
            log.warning(f"Safety check triggered for critical command: '{matched_key}'")
            
            # If running inside CustomTkinter GUI, invoke GUI confirmation window
            if confirmation_callback:
                approved = confirmation_callback(matched_key)
                if not approved:
                    log.info(f"Critical command '{matched_key}' rejected via GUI callback.")
                    return False
            else:
                # Terminal fallback for confirmation
                print(f"\n[WARNING] You are attempting to run a critical command: '{matched_key}'")
                confirm = input("Are you sure you want to execute this? (yes/no): ").strip().lower()
                if confirm not in ['y', 'yes']:
                    print("[ERROR] Command cancelled by user.")
                    return False
                    
        log.info(f"Asynchronously executing shell command: '{shell_command}'")
        try:
            # Asynchronous Popen execution ensures the Python engine and GUI stay highly responsive
            subprocess.Popen(shell_command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception as e:
            log.error(f"Failed to execute command '{shell_command}': {e}")
            return False

    def run_cycle(self, tts_method=None, voice_name=None, confirmation_callback=None):
        """
        Executes a single Speech-to-Speech loop cycle:
        1. Capture speech using STT.
        2. Perform fast command matching.
        3. Fallback to Name Greeting or Echo.
        4. Synthesize voice response using TTS.
        
        Returns a dict of results: {"user_text": ..., "response": ..., "command_executed": ..., "latency_ms": ...}
        """
        log.info("Speech-to-Speech cycle started.")
        cycle_start = time.perf_counter()
        
        # Step 1: Run STT to capture voice input
        user_input = run_stt()
        
        if not user_input:
            response = "Sorry, I didn't hear anything. Please try again."
            self.tts.speak(response, method=tts_method, voice_name=voice_name)
            latency_ms = (time.perf_counter() - cycle_start) * 1000.0
            return {
                "user_text": None,
                "response": response,
                "command_executed": None,
                "latency_ms": latency_ms
            }
            
        # Step 2: High-Performance Command Matching
        matched_key, shell_command = self.match_command(user_input)
        
        if matched_key:
            if shell_command.startswith("py:"):
                # Execute native control and get dynamic voice response
                success, response = self.execute_python_command(shell_command)
                log.info(f"Native command execution: '{matched_key}' -> '{shell_command}' -> Success: {success}, Resp: '{response}'")
                
                # Speak the dynamic outcome response
                self.tts.speak(response, method=tts_method, voice_name=voice_name)
                
                latency_ms = (time.perf_counter() - cycle_start) * 1000.0
                return {
                    "user_text": user_input,
                    "response": response,
                    "command_executed": matched_key,
                    "latency_ms": latency_ms
                }
            else:
                response = f"Executing command: {matched_key}."
                log.info(f"Command execution match: '{matched_key}' -> '{shell_command}'")
                
                # Speak response first (or simultaneously)
                self.tts.speak(response, method=tts_method, voice_name=voice_name)
                
                # Execute command asynchronously
                self.execute_command(shell_command, matched_key, confirmation_callback)
                
                latency_ms = (time.perf_counter() - cycle_start) * 1000.0
                return {
                    "user_text": user_input,
                    "response": response,
                    "command_executed": matched_key,
                    "latency_ms": latency_ms
                }
            
        # Step 3: Conversational fallback (Name matching or Echo)
        greeting = extract_name_and_greet(user_input)
        if greeting:
            response = greeting
        else:
            response = f"I heard you say: {user_input}"
            
        log.info(f"Conversational response: [User: '{user_input}'] -> [Assistant: '{response}']")
        self.tts.speak(response, method=tts_method, voice_name=voice_name)
        
        latency_ms = (time.perf_counter() - cycle_start) * 1000.0
        return {
            "user_text": user_input,
            "response": response,
            "command_executed": None,
            "latency_ms": latency_ms
        }

    def run_cycle_async(self, callback=None, confirmation_callback=None, tts_method=None, voice_name=None):
        """
        Runs the Speech-to-Speech cycle asynchronously in a separate daemon thread.
        This keeps the CustomTkinter GUI responsive.
        
        Parameters:
            callback: Function called upon loop completion, passing the result dict.
            confirmation_callback: Function called to show CustomTkinter confirmation popups.
        """
        # Stop any active voice playback before starting a cycle
        self.stop()
        
        def thread_target():
            results = self.run_cycle(
                tts_method=tts_method, 
                voice_name=voice_name, 
                confirmation_callback=confirmation_callback
            )
            if callback:
                try:
                    callback(results)
                except Exception as e:
                    log.error(f"Error in Speech-to-Speech callback: {e}")
                    
        s2s_thread = threading.Thread(target=thread_target, daemon=True)
        s2s_thread.start()
        return s2s_thread

    def stop(self):
        """Instantly interrupts any ongoing speech playback."""
        self.tts.stop()

    def execute_python_command(self, py_command):
        """
        Executes internal Python system control operations.
        Format: 'py:<action>' or 'py:<action>:<param>'
        Returns a tuple (success: bool, message: str)
        """
        try:
            from core.automation import SystemController
            parts = py_command.split(":")
            action = parts[1]
            
            if action == "volume_up":
                return True, SystemController.change_volume(10)
            elif action == "volume_down":
                return True, SystemController.change_volume(-10)
            elif action == "mute":
                return True, SystemController.set_mute(True)
            elif action == "unmute":
                return True, SystemController.set_mute(False)
            elif action == "brightness_up":
                return True, SystemController.change_brightness(10)
            elif action == "brightness_down":
                return True, SystemController.change_brightness(-10)
            elif action == "set_volume":
                param = int(parts[2])
                return True, SystemController.set_volume(param)
            elif action == "set_brightness":
                param = int(parts[2])
                return True, SystemController.set_brightness(param)
            else:
                return False, f"Unknown native system control action: {action}"
        except Exception as e:
            log.error(f"Error executing native system control: {e}")
            return False, f"Failed to execute system control: {e}"


# Self-test block
if __name__ == "__main__":
    print("\n=== LOQ Speech-to-Speech Command Execution Test ===")
    print("This will execute a single end-to-end voice command cycle.")
    print("Try saying: 'open notepad', 'open calculator', or 'hello, my name is John'.")
    
    system = SpeechToSpeechSystem(tts_method="pyttsx3")
    results = system.run_cycle()
    
    print("\n--- Cycle Completed ---")
    print(f"User Spoke: {results['user_text']}")
    print(f"Assistant Replied: {results['response']}")
    print(f"Command Executed: {results['command_executed']}")

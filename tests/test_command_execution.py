"""
Test Command Execution Script for Personal Assistant (LOQ).
Demonstrates and tests the high-performance dictionary lookup + pre-compiled Regex
matching approach for system command execution without blocking the main loop.
"""

import os
import sys
import re
import json
import subprocess
import time

# Add project root to sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from utils.logger import logging as log

class CommandExecutor:
    def __init__(self, commands_config_path=None):
        if not commands_config_path:
            commands_config_path = os.path.join(project_root, "config", "commands.json")
            
        self.commands_path = commands_config_path
        self.commands = {}
        self.command_regex = None
        self.critical_commands = ["shutdown", "restart", "sleep", "hibernate", "del", "delete"]
        
        self.load_commands()

    def load_commands(self):
        """Loads command mappings from JSON and compiles regex matcher."""
        try:
            if not os.path.exists(self.commands_path):
                log.error(f"Commands config not found at: {self.commands_path}")
                print(f"Error: Commands config not found at {self.commands_path}")
                return False
                
            with open(self.commands_path, "r") as f:
                self.commands = json.load(f)
                
            log.info(f"Loaded {len(self.commands)} system commands from config.")
            
            # Sort command keys by length descending to match longer specific keys first
            # E.g., "open powershell as admin" should match before "open powershell"
            sorted_keys = sorted(self.commands.keys(), key=len, reverse=True)
            
            # Create a combined regex pattern for word-boundary matching
            pattern = r"\b(" + "|".join(re.escape(k) for k in sorted_keys) + r")\b"
            self.command_regex = re.compile(pattern, re.IGNORECASE)
            log.info("Successfully pre-compiled command matching regex pattern.")
            return True
        except Exception as e:
            log.error(f"Error loading commands: {e}")
            print(f"Error loading commands: {e}")
            return False

    def clean_input(self, text):
        """Cleans user input to improve matching precision, resolving synonyms and stripping filler words."""
        if not text:
            return ""
        # 1. Lowercase and strip
        text = text.lower().strip()
        
        # 2. Remove common punctuation
        text = re.sub(r"[.,\/#!$%\^&\*;:{}=\-_`~()?]", "", text)
        
        # 3. Standard text normalizations / synonym mapping
        text = text.replace("shut down", "shutdown")
        text = text.replace("wi fi", "wifi")
        text = text.replace("wi-fi", "wifi")
        text = text.replace("signout", "sign out")
        
        # 4. Remove conversational filler words
        filler_words = {"please", "could", "you", "can", "hey", "loq", "the", "a", "an", "now", "right", "want", "would", "like"}
        words = text.split()
        filtered_words = [w for w in words if w not in filler_words]
        
        cleaned = " ".join(filtered_words)
        return cleaned

    def match_command(self, user_input):
        """
        Matches user speech to a system command using pre-compiled regex.
        Returns the matched command key and the shell command, or (None, None).
        """
        cleaned = self.clean_input(user_input)
        if not cleaned:
            return None, None
            
        start_time = time.perf_counter()
        
        # 1. Try exact dictionary hit first (O(1))
        if cleaned in self.commands:
            latency = (time.perf_counter() - start_time) * 1_000_000
            log.info(f"Exact match found for '{cleaned}' in {latency:.2f} microseconds.")
            return cleaned, self.commands[cleaned]
            
        # 2. Fallback to Regex search (O(L) string scan in C)
        match = self.command_regex.search(cleaned)
        latency = (time.perf_counter() - start_time) * 1_000_000
        
        if match:
            matched_key = match.group(1).lower()
            shell_command = self.commands.get(matched_key)
            log.info(f"Regex match found: '{matched_key}' inside user text in {latency:.2f} microseconds.")
            return matched_key, shell_command
            
        log.info(f"No command match found for: '{cleaned}' (Time: {latency:.2f} μs)")
        return None, None

    def is_critical(self, matched_key):
        """Checks if a command requires user safety confirmation."""
        return any(keyword in matched_key for keyword in self.critical_commands)

    def execute(self, shell_command, matched_key=None, skip_safety=False):
        """
        Executes a shell command asynchronously in the background.
        If the command is critical, prompts for user confirmation first.
        """
        if not shell_command:
            return False
            
        # Check safety and confirmation
        if matched_key and self.is_critical(matched_key) and not skip_safety:
            print(f"\n[WARNING] You are attempting to run a critical command: '{matched_key}'")
            confirm = input("Are you sure you want to execute this? (yes/no): ").strip().lower()
            if confirm not in ['y', 'yes']:
                print("[ERROR] Command cancelled by user.")
                log.info(f"Critical command '{matched_key}' execution cancelled by user.")
                return False
                
        log.info(f"Executing shell command: '{shell_command}'")
        print(f"[RUNNING] Command: {shell_command}")
        
        try:
            # Popen executes asynchronously, meaning it won't freeze python or GUI
            # while the launched app runs!
            subprocess.Popen(shell_command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception as e:
            log.error(f"Failed to execute command '{shell_command}': {e}")
            print(f"[ERROR] Execution failed: {e}")
            return False


if __name__ == "__main__":
    print("=== LOQ Command Matcher & Executor Test ===")
    executor = CommandExecutor()
    
    print("\n--- Test Suite 1: Latency and Match Correctness ---")
    test_cases = [
        "open chrome",                                  # Exact match
        "please open vscode right now",                 # Embedded sentence
        "could you open powershell as admin please",    # Long matching priority
        "open terminal",                                # Baseline
        "hey loq, please shut down the pc",             # Critical command with noise
        "invalid command sentence"                      # No match
    ]
    
    for case in test_cases:
        print(f"\nUser Input: \"{case}\"")
        matched_key, cmd = executor.match_command(case)
        if matched_key:
            print(f"Matched Key: '{matched_key}'")
            print(f"Shell Command: '{cmd}'")
            if executor.is_critical(matched_key):
                print("Critical Status: [WARNING] Critical command detected!")
        else:
            print("Matched Key: None")

    print("\n--- Test Suite 2: Interactive Tester ---")
    print("Type sentences below to test execution (e.g. 'open notepad', 'open calculator', 'check ip address').")
    print("Press Ctrl+C or type 'exit' to quit.")
    
    while True:
        try:
            user_input = input("\nEnter voice test string: ").strip()
            if user_input.lower() == 'exit':
                break
            if not user_input:
                continue
                
            matched_key, cmd = executor.match_command(user_input)
            if matched_key:
                print(f"Matched: '{matched_key}' -> '{cmd}'")
                # Execute command (safety is checked inside)
                executor.execute(cmd, matched_key)
            else:
                print("[ERROR] No matching command found in commands.json.")
        except KeyboardInterrupt:
            print("\nExiting interactive test.")
            break

"""
Text-to-Speech (TTS) Engine Module for Personal Assistant (LOQ).
Supports Pyttsx3 (Offline), gTTS (Google Cloud-based free), and ElevenLabs (Premium Cloud-based).
Designed to be fully compatible and safe for multithreading in a CustomTkinter GUI application.
"""

import os
import sys
import threading
import ctypes
import json
from dotenv import load_dotenv

# Add project root to sys.path to ensure absolute imports work correctly
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from utils.logger import logging as log

# ----------------- Windows Audio Playback (MCI) -----------------
# This allows playing MP3/WAV files completely asynchronously in the background,
# and allows us to interrupt/stop the audio instantly from the GUI.
def play_audio_windows(file_path):
    """Plays an audio file asynchronously on Windows using MCI (Media Control Interface)."""
    try:
        # Convert path to absolute to avoid relative path issues in Windows API
        abs_path = os.path.abspath(file_path)
        
        # Stop and close any previous playback under the alias 'loq_tts'
        ctypes.windll.winmm.mciSendStringW("stop loq_tts", None, 0, 0)
        ctypes.windll.winmm.mciSendStringW("close loq_tts", None, 0, 0)
        
        # Open the file
        open_cmd = f'open "{abs_path}" type mpegvideo alias loq_tts'
        res = ctypes.windll.winmm.mciSendStringW(open_cmd, None, 0, 0)
        if res != 0:
            log.error(f"MCI open failed for {abs_path} with code {res}")
            return False
            
        # Play the audio in the background (asynchronously)
        play_cmd = "play loq_tts"
        res = ctypes.windll.winmm.mciSendStringW(play_cmd, None, 0, 0)
        if res != 0:
            log.error(f"MCI play failed with code {res}")
            return False
            
        log.info(f"Asynchronously playing TTS audio: {file_path}")
        return True
    except Exception as e:
        log.error(f"Exception during MCI playback: {e}")
        return False

def stop_audio_windows():
    """Instantly stops any background audio playback."""
    try:
        ctypes.windll.winmm.mciSendStringW("stop loq_tts", None, 0, 0)
        ctypes.windll.winmm.mciSendStringW("close loq_tts", None, 0, 0)
        log.info("Stopped active background audio playback.")
    except Exception as e:
        log.error(f"Exception stopping audio playback: {e}")


# ----------------- Core Speech Functions -----------------

def speak_pyttsx3(text, rate=180, voice_index=0):
    """
    Offline Text-to-Speech using pyttsx3.
    Note: Highly responsive, does not require internet, completely free.
    """
    try:
        import pyttsx3
        # Initialize engine inside the function/thread to avoid COM threading issues
        engine = pyttsx3.init()
        engine.setProperty('rate', rate)
        
        voices = engine.getProperty('voices')
        if voices and voice_index < len(voices):
            engine.setProperty('voice', voices[voice_index].id)
            
        log.info(f"Speaking offline via pyttsx3: '{text}'")
        engine.say(text)
        engine.runAndWait()
        return True
    except Exception as e:
        log.error(f"pyttsx3 execution error: {e}")
        return False


def speak_gtts(text, lang='en', output_file='temp_gtts.mp3'):
    """
    Free Cloud-based Text-to-Speech using gTTS (Google Translate TTS).
    Saves to an mp3 file and plays it asynchronously.
    """
    try:
        from gtts import gTTS
        log.info(f"Generating gTTS speech for: '{text}'")
        
        # Stop and close previous playback to release the Windows MCI file lock
        stop_audio_windows()
        
        # Generate the audio file
        tts = gTTS(text=text, lang=lang)
        tts.save(output_file)
        
        # Play the audio in a background thread using MCI
        return play_audio_windows(output_file)
    except Exception as e:
        log.error(f"gTTS execution error: {e}")
        return False


def speak_elevenlabs(text, voice_id=None, model_id="eleven_multilingual_v2", output_file="temp_elevenlabs.mp3"):
    """
    Premium Cloud-based Text-to-Speech using ElevenLabs API.
    Saves to an mp3 file and plays it asynchronously.
    """
    try:
        from elevenlabs.client import ElevenLabs
        load_dotenv()
        
        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            log.error("ElevenLabs API Key not found in environment variables.")
            # Trigger pyttsx3 fallback if desired, or return False
            return False
            
        client = ElevenLabs(api_key=api_key)
        
        # Fallback to standard voice ID if none is supplied
        if not voice_id:
            voice_id = "cgSgspJ2msm6clMCkdW9" # Default voice ID
            
        log.info(f"Generating ElevenLabs premium speech for: '{text}' using voice ID: {voice_id}")
        
        # Stop and close previous playback to release the Windows MCI file lock
        stop_audio_windows()
        
        # Request speech conversion
        audio_generator = client.text_to_speech.convert(
            voice_id=voice_id,
            output_format="mp3_44100_128",
            text=text,
            model_id=model_id
        )
        
        # Read the generator and write the bytes to an MP3 file
        with open(output_file, "wb") as f:
            for chunk in audio_generator:
                f.write(chunk)
                
        # Play the audio in a background thread using MCI
        return play_audio_windows(output_file)
    except Exception as e:
        log.error(f"ElevenLabs execution error: {e}")
        return False


# ----------------- Configuration & Settings Helpers -----------------

def get_voice_id_by_name(voice_name):
    """Utility to retrieve the ElevenLabs voice ID corresponding to a name from settings.json."""
    try:
        config_path = os.path.join(project_root, "config", "settings.json")
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                data = json.load(f)
            voice_models = data.get("Voice Model", [])
            for item in voice_models:
                if voice_name in item:
                    return item[voice_name]
    except Exception as e:
        log.error(f"Error loading voice_id from config: {e}")
    return None


def check_wifi(host="8.8.8.8", port=53, timeout=2):
    """Checks for active internet connection via socket."""
    try:
        import socket
        socket.create_connection((host, port), timeout=timeout)
        return True
    except OSError:
        pass
    return False


# ----------------- Unified CustomTkinter-Ready Controller Class -----------------

class TTSEngine:
    """
    A stateful, thread-safe manager for all three TTS options.
    Ideal for direct importing and usage inside a CustomTkinter GUI.
    """
    def __init__(self, default_method="pyttsx3", voice_name="Jessica"):
        self.default_method = default_method
        self.voice_name = voice_name
        self._current_thread = None

    def speak(self, text, method=None, voice_name=None):
        """
        Synchronous wrapper that executes the chosen TTS generation method.
        Should generally be run via speak_async inside CustomTkinter.
        """
        method = method or self.default_method
        voice_name = voice_name or self.voice_name
        method = method.lower()
        
        log.info(f"TTS requested: '{text}' [Method: {method}]")

        # Fallback if no WiFi is detected for cloud-based methods
        if method in ["elevenlabs", "gtts"] and not check_wifi():
            log.warning("No WiFi detected. Falling back to offline Pyttsx3.")
            method = "pyttsx3"

        if method == "elevenlabs":
            voice_id = get_voice_id_by_name(voice_name)
            success = speak_elevenlabs(text, voice_id=voice_id)
            if not success:
                log.warning("ElevenLabs failed or was unconfigured. Falling back to gTTS.")
                method = "gtts"
                
        if method == "gtts":
            success = speak_gtts(text)
            if not success:
                log.warning("gTTS failed. Falling back to offline Pyttsx3.")
                method = "pyttsx3"

        if method == "pyttsx3":
            # Pyttsx3 has simple index-based voices (0: Male, 1: Female standard on Win)
            # Default to index 1 (Female) to match the assistant theme or 0 as default
            voice_index = 1 if voice_name.lower() in ["lily", "jessica"] else 0
            speak_pyttsx3(text, voice_index=voice_index)

    def speak_async(self, text, method=None, voice_name=None):
        """
        Asynchronously runs the TTS engine in a background thread.
        CRITICAL: Use this function in your CustomTkinter app to prevent UI freezing!
        """
        # Stop any audio playback currently playing before starting the next one
        self.stop()
        
        # Start a new daemon thread to speak
        self._current_thread = threading.Thread(
            target=self.speak, 
            args=(text, method, voice_name),
            daemon=True
        )
        self._current_thread.start()
        return self._current_thread

    def stop(self):
        """Instantly terminates any active audio playback (MCI)."""
        stop_audio_windows()


# Self-test code
if __name__ == "__main__":
    print("Testing TTS Engine...")
    engine = TTSEngine()
    
    # Test offline pyttsx3
    print("Speaking via offline pyttsx3...")
    engine.speak("Testing offline system voice.", method="pyttsx3")
    
    # Test gTTS
    print("Speaking via gTTS...")
    engine.speak("Testing google text to speech.", method="gtts")
    
    # Test ElevenLabs (requires key)
    # print("Speaking via ElevenLabs...")
    # engine.speak("Testing eleven labs premium voice.", method="elevenlabs")
    
    print("TTS test complete.")
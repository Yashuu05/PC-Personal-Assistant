import pyaudio
import numpy as np
import time
from openwakeword.model import Model
from utils.logger import logging as log

class WakeWordEngine:
    def __init__(self, wake_word="hey jarvis", confidence_threshold=0.4):
        self.wake_word = wake_word
        self.confidence_threshold = confidence_threshold
        try:
            import os
            # Try loading the downloaded local model
            model_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", f"{self.wake_word}_v0.1.onnx"))
            if os.path.exists(model_path):
                self.model = Model(wakeword_models=[model_path], inference_framework="onnx")
                log.info(f"Successfully loaded openWakeWord model from path: {model_path}")
            else:
                self.model = Model(wakeword_models=[self.wake_word])
                log.info(f"Successfully loaded openWakeWord model from default library path: {self.wake_word}")
        except Exception as e:
            log.error(f"Failed to load openWakeWord model: {e}")
            self.model = None

    def listen(self, callback, stop_event, pause_event):
        """
        Listens continuously on a low-overhead PyAudio stream.
        Triggers callback when the target wake word is spoken.
        stop_event: threading.Event to exit the loop entirely.
        pause_event: threading.Event to temporarily pause processing audio (e.g. while STT is running).
        """
        if not self.model:
            log.error("WakeWord model not loaded. Exiting listener.")
            return

        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        CHUNK = 1280

        audio = pyaudio.PyAudio()
        try:
            mic_stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, 
                                    input=True, frames_per_buffer=CHUNK)
        except Exception as e:
            log.error(f"Failed to open PyAudio stream for WakeWord: {e}")
            audio.terminate()
            return
            
        log.info(f"Wake word listener background loop started.")
        
        try:
            while not stop_event.is_set():
                if pause_event.is_set():
                    # If paused, sleep briefly to avoid burning CPU and clear stream buffer
                    time.sleep(0.1)
                    if mic_stream.is_active():
                        try:
                            # clear the incoming data so it doesn't build up
                            mic_stream.read(mic_stream.get_read_available(), exception_on_overflow=False)
                        except Exception:
                            pass
                    continue
                
                # Read mic data
                data = mic_stream.read(CHUNK, exception_on_overflow=False)
                audio_frame = np.frombuffer(data, dtype=np.int16)
                
                # Feed into openWakeWord
                self.model.predict(audio_frame)
                
                # Check confidence
                for mdl in self.model.prediction_buffer.keys():
                    scores = list(self.model.prediction_buffer[mdl])
                    if scores and scores[-1] > self.confidence_threshold:
                        log.info(f"Wake word '{mdl}' detected!")
                        if callback:
                            callback()
                        # Reset buffer after trigger to prevent multiple immediate triggers
                        self.model.reset()
                        # Short pause to allow system to react
                        time.sleep(1.0)
                        
        except Exception as e:
            log.error(f"Error in WakeWord loop: {e}")
        finally:
            if mic_stream.is_active():
                mic_stream.stop_stream()
            mic_stream.close()
            audio.terminate()
            log.info("Wake word listener stopped.")

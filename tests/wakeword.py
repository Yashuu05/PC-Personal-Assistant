import pyaudio
import numpy as np
import time
import os
import sys

# Add project root to sys.path to allow importing from utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import logging as log
from openwakeword.model import Model

def test_wakeword():
    wake_word = "hey jarvis"
    model_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", f"hey_jarvis_v0.1.onnx"))
    
    log.info(f"Loading openwakeword model from {model_path}...")
    print(f"Loading openwakeword model from {model_path}...")
    
    if not os.path.exists(model_path):
        error_msg = f"Model not found at {model_path}. Please ensure the model exists."
        log.error(error_msg)
        print(error_msg)
        return
        
    try:
        model = Model(wakeword_models=[model_path], inference_framework="onnx")
        log.info("Model loaded successfully.")
    except Exception as e:
        error_msg = f"Failed to load openWakeWord model: {e}"
        log.error(error_msg)
        print(error_msg)
        return

    # PyAudio configuration
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1280

    audio = pyaudio.PyAudio()
    try:
        mic_stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    except Exception as e:
        error_msg = f"Failed to open PyAudio stream: {e}"
        log.error(error_msg)
        print(error_msg)
        audio.terminate()
        return
    
    log.info("Started listening for 'hey jarvis'...")
    print("\nListening for 'hey jarvis' (Press Ctrl+C to stop)...")
    
    confidence_threshold = 0.3

    try:
        chunk_count = 0
        while True:
            # Read mic data
            data = mic_stream.read(CHUNK, exception_on_overflow=False)
            audio_frame = np.frombuffer(data, dtype=np.int16)
            
            # Feed into openWakeWord
            model.predict(audio_frame)
            chunk_count += 1
            
            if chunk_count % 50 == 0:
                print(f"Debug: processed {chunk_count} chunks. Still listening...")
            
            # Check confidence scores
            for mdl in model.prediction_buffer.keys():
                scores = list(model.prediction_buffer[mdl])
                if scores:
                    score = scores[-1]
                    
                    if score > 0.05:
                        print(f"Debug [{mdl}]: Score = {score:.4f}")
                        
                    if score > confidence_threshold:
                        msg = f"listening, wakeword detected. Confidence score: {score:.4f}"
                        log.info(msg)
                        print(f"\n{msg}")
                        
                        # Reset buffer after trigger to prevent multiple immediate triggers
                        model.reset()
                        time.sleep(1.0)
                        
                        print("\nListening for 'hey jarvis' (Press Ctrl+C to stop)...")
                        
    except KeyboardInterrupt:
        log.info("Testing stopped by user.")
        print("\nTesting stopped by user.")
    except Exception as e:
        error_msg = f"Error during execution: {e}"
        log.error(error_msg)
        print(f"Error: {error_msg}")
    finally:
        if 'mic_stream' in locals() and mic_stream.is_active():
            mic_stream.stop_stream()
            mic_stream.close()
        audio.terminate()

if __name__ == "__main__":
    test_wakeword()

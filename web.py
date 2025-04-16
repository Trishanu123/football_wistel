import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import sounddevice as sd
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ESP32 IP Address - MAKE SURE THIS IS CORRECT
ESP32_IP = 'http://192.168.0.5'  # <- Verify this matches your ESP32's actual IP

# Configure requests with retry strategy
session = requests.Session()
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

# Load YAMNet class map
class_map_path = tf.keras.utils.get_file(
    'yamnet_class_map.csv',
    'https://raw.githubusercontent.com/tensorflow/models/master/research/audioset/yamnet/yamnet_class_map.csv'
)
class_names = [line.strip().split(',')[2] for line in open(class_map_path).readlines()[1:]]

# Load YAMNet model from TF Hub
yamnet_model = hub.load('https://tfhub.dev/google/yamnet/1')

# Function to record audio
def record_audio(duration=2, sample_rate=16000):
    # Reset the audio stream before recording
    sd.stop()
    # Add a small delay to allow audio device to reset
    time.sleep(0.1)
    
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
    sd.wait()
    return audio.flatten()

# Update whistle status on ESP32 with robust error handling
def update_esp32_status(whistle_detected):
    status = "detected" if whistle_detected else "clear"
    url = f'{ESP32_IP}/whistle/{status}'
    
    try:
        # Use the session with retry strategy
        response = session.get(url, timeout=5.0)
        print(f"ESP32 status updated: {'Whistle detected' if whistle_detected else 'No whistle'}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Connection to ESP32 failed: {e}")
        return False

# Simple connectivity check
def check_esp32_connection():
    print("Testing connection to ESP32...")
    try:
        session.get(f'{ESP32_IP}/', timeout=5.0)
        print("✅ Connection to ESP32 successful")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to ESP32: {e}")
        print("Please verify the ESP32 IP address and make sure it's on the same network")
        return False

# Whistle detection loop
def detect_whistle_loop():
    print("🚀 Listening for whistles... (Press Ctrl+C to stop)\n")
    whistle_detected = False
    cooldown_counter = 0
    update_interval = 0
    
    # First, check if we can connect to the ESP32
    if not check_esp32_connection():
        print("Please fix the connection issues and restart the script")
        return
    
    try:
        while True:
            # Record audio
            waveform = record_audio(duration=1.5)
            
            # Only process if audio contains meaningful data
            if np.abs(waveform).max() > 0.01:
                # Get predictions
                scores, _, _ = yamnet_model(waveform)
                mean_scores = np.mean(scores.numpy(), axis=0)
                top5_idx = np.argsort(mean_scores)[::-1][:5]
                top5_labels = [class_names[i] for i in top5_idx]
                
                # Print top detected sounds for debugging
                top_sound = class_names[np.argmax(mean_scores)]
                whistle_score = mean_scores[class_names.index('Whistling')] if 'Whistling' in class_names else 0
                print(f"Top sound: {top_sound} | Whistle confidence: {whistle_score:.4f}")
                
                # Detect whistle with improved logic
                if 'Whistling' in top5_labels and mean_scores[class_names.index('Whistling')] > 0.1:
                    if not whistle_detected:
                        print("🎯 Whistle detected!")
                        update_esp32_status(True)
                        whistle_detected = True
                        cooldown_counter = 4
                        update_interval = 0
                elif cooldown_counter <= 0:
                    if whistle_detected:
                        update_esp32_status(False)
                        whistle_detected = False
                        update_interval = 0
            
            # Send periodic status updates to keep the connection alive
            update_interval += 1
            if update_interval >= 15:  # Send a status update every ~15 cycles
                update_esp32_status(whistle_detected)
                update_interval = 0
            
            # Decrease cooldown counter if active
            if cooldown_counter > 0:
                cooldown_counter -= 1
                
            # Increased delay to reduce network load
            time.sleep(1.0)  # Increased to 1 second
            
    except KeyboardInterrupt:
        print("\n🛑 Stopped listening.")
        # Clear signal when exiting
        update_esp32_status(False)

# Run it
if __name__ == "__main__":
    detect_whistle_loop()
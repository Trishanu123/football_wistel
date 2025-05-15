import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import sounddevice as sd
import time

# Load YAMNet class labels
class_map_path = tf.keras.utils.get_file(
    'yamnet_class_map.csv',
    'https://raw.githubusercontent.com/tensorflow/models/master/research/audioset/yamnet/yamnet_class_map.csv'
)
class_names = [line.strip().split(',')[2] for line in open(class_map_path).readlines()[1:]]

# Load YAMNet model
yamnet_model = hub.load('https://tfhub.dev/google/yamnet/1')

# Function to record audio
def record_audio(duration=1.5, sample_rate=16000):
    sd.stop()
    time.sleep(0.1)
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
    sd.wait()
    return audio.flatten()

# Function to detect whistle
def detect_whistle(audio_data):
    scores, _, _ = yamnet_model(audio_data)
    mean_scores = np.mean(scores.numpy(), axis=0)
    
    # Get the index of the "Whistling" class
    if 'Whistling' in class_names:
        whistle_index = class_names.index('Whistling')
        confidence = mean_scores[whistle_index]
        return confidence
    return 0.0

# Whistle detection loop
def start_whistle_detection(threshold=0.1):
    print("🎧 Listening for whistle sounds (Press Ctrl+C to stop)...\n")
    try:
        while True:
            audio = record_audio()
            if np.abs(audio).max() > 0.01:  # Filter out silence
                whistle_confidence = detect_whistle(audio)
                print(f"🔍 Whistle Confidence: {whistle_confidence:.4f}")
                if whistle_confidence > threshold:
                    print("🎯 Whistle Detected!")
            time.sleep(0.5)  # Adjust for performance
    except KeyboardInterrupt:
        print("\n🛑 Detection stopped.")

start_whistle_detection()

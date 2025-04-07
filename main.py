import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import sounddevice as sd
import time

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
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
    sd.wait()
    return audio.flatten()

# Whistle detection loop
def detect_whistle_loop():
    print("🚀 Listening for whistles... (Press Ctrl+C to stop)\n")
    try:
        while True:
            waveform = record_audio(duration=2)

            # Get predictions
            scores, _, _ = yamnet_model(waveform)
            mean_scores = np.mean(scores.numpy(), axis=0)
            top5_idx = np.argsort(mean_scores)[::-1][:5]
            top5_labels = [class_names[i] for i in top5_idx]

            if 'Whistling' in top5_labels:
                print("🎯 Whistle detected!")
            else:
                pass  # Stay silent for all other sounds

            time.sleep(0.1)  # Slight delay to prevent overloading the CPU
    except KeyboardInterrupt:
        print("\n🛑 Stopped listening.")

# Run it
detect_whistle_loop()

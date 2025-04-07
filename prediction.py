import librosa
import numpy as np
import sounddevice as sd
import tensorflow as tf
import librosa.display
import time

# Load trained model
model = tf.keras.models.load_model("whistle_model.h5")

# Function to record audio from the microphone
def record_audio(duration=5, sr=22050):
    print("🎤 Recording... Whistle now!")
    audio = sd.rec(int(duration * sr), samplerate=sr, channels=1, dtype="float32")
    sd.wait()  # Wait until recording is finished
    print("✅ Recording complete!")
    return audio.flatten(), sr

# Convert audio to Mel Spectrogram
def audio_to_spectrogram(audio, sr, fixed_length=100):
    mel_spec = librosa.feature.melspectrogram(y=audio, sr=sr, n_mels=128)
    mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)

    # Pad or truncate to fixed length
    if mel_spec_db.shape[1] < fixed_length:
        pad_width = fixed_length - mel_spec_db.shape[1]
        mel_spec_db = np.pad(mel_spec_db, ((0, 0), (0, pad_width)), mode="constant")
    else:
        mel_spec_db = mel_spec_db[:, :fixed_length]

    return mel_spec_db

# Predict whistle
def predict_whistle(threshold=0.5):
    audio, sr = record_audio()

    # Play back the audio
    print("🔁 Playing back the audio...")
    sd.play(audio, sr)
    sd.wait()

    # Convert to spectrogram
    spectrogram = audio_to_spectrogram(audio, sr)

    # Normalize and reshape
    spectrogram = spectrogram / np.max(spectrogram)
    spectrogram = np.expand_dims(spectrogram, axis=-1)  # Shape: (128, 100, 1)
    spectrogram = np.expand_dims(spectrogram, axis=0)   # Shape: (1, 128, 100, 1)

    # Check shape match with model
    print("📏 Input shape to model:", spectrogram.shape)

    # Make prediction
    prob = model.predict(spectrogram)[0][0]
    print(f"📊 Prediction probability: {prob:.4f}")

    if prob > threshold:
        label = "Start Whistle"
    else:
        label = "Stop Whistle"

    print(f"🧐 Predicted: {label}")

# Run prediction
if __name__ == "__main__":
    while True:
        predict_whistle(threshold=0.5)
        time.sleep(2)

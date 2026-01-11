import os
import queue
import sounddevice as sd
import soundfile as sf
import numpy as np
from pynput import keyboard
from src.transcribe import transcriber

# Configuration
AUDIO_PATH = "data/audio_temp/recording.wav"
SAMPLE_RATE = 16000  # Whisper prefers 16kHz
CHANNELS = 1

class Recorder:
    def __init__(self):
        self.recording = False
        self.audio_data = []

    def start(self):
        self.recording = True
        self.audio_data = []
        print("\n🔴 Recording... Speak now!")

    def stop(self):
        self.recording = False
        # Save the recorded data to a file
        if self.audio_data:
            audio_array = np.concatenate(self.audio_data, axis=0)
            sf.write(AUDIO_PATH, audio_array, SAMPLE_RATE)
            print(f"✅ Saved to {AUDIO_PATH}")

    def callback(self, indata, frames, time, status):
        if self.recording:
            self.audio_data.append(indata.copy())

recorder = Recorder()

def main():
    if not os.path.exists("data/audio_temp"):
        os.makedirs("data/audio_temp")

    print("💪 Iron Log Station Ready.")
    print("HOLD [SPACE] to record. Press [ESC] to quit.")

    # Setup the audio stream (this will wait for your mic)
    # We wrap it in a try-except so it doesn't crash without a mic
    try:
        stream = sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, callback=recorder.callback)
        stream.start()
    except Exception as e:
        print(f"⚠️  Microphone Note: {e} (Recording will be simulated)")

    def on_press(key):
        if key == keyboard.Key.esc:
            return False
        if key == keyboard.Key.space and not recorder.recording:
            recorder.start()
            
    def on_release(key):
        if key == keyboard.Key.space:
            recorder.stop()
            
            # --- REAL TRANSCRIPTION ---
            print("⏳ Transcribing on Pi 5...")
            # If no mic, we use the mock text. If mic exists, we use real file.
            if os.path.exists(AUDIO_PATH):
                # ... inside your key release logic ...
                text, confidence = transcriber.transcribe(AUDIO_PATH)
                print(f"Detected: {text} (Confidence: {confidence:.2f})")
                
            else:
                text = "Bodyweight eighty five point two kilos."
            
            print(f"🗣️  Heard: '{text}'")

            # --- NEXT STEP: EXTRACTION ---
            print("🧠 Extracting data (Next Step)...")
            # mock_data = extract_data(text)
            
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

if __name__ == "__main__":
    main()
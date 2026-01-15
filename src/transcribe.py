"""Local transcription via faster-whisper optimized for Raspberry Pi 5."""
from __future__ import annotations
from pathlib import Path
from typing import Tuple
import logging

from faster_whisper import WhisperModel

# Optional: suppress some of the verbose logging from faster-whisper
logging.getLogger("faster_whisper").setLevel(logging.ERROR)

class Transcriber:
    def __init__(self, model_size: str = "small"):
        """
        Initializes and keeps the model in memory.
        - small: Best balance for accuracy in German on Pi 5.
        - base: Faster alternative if 'small' is too slow.
        - device="cpu": Pi 5 doesn't have a CUDA GPU.
        - compute_type="int8": Critical for performance on ARM CPUs.
        """
        print(f"Loading Whisper model ({model_size})...")
        self.model = WhisperModel(
            model_size, 
            device="cpu", 
            compute_type="int8"
        )

    def transcribe(self, wav_path: Path) -> Tuple[str, float]:
        """Transcribe the file using the pre-loaded model."""
        # beam_size=1 is fast; beam_size=5 is more accurate.
        # language="de" forces German detection, which is more reliable for short clips.
        segments, info = self.model.transcribe(str(wav_path), beam_size=1, language="de")
        
        text_parts = []
        probs = []
        
        for seg in segments:
            text_parts.append(seg.text)
            probs.append(seg.avg_logprob)
            
        text = " ".join(t.strip() for t in text_parts).strip()
        avg_prob = sum(probs) / len(probs) if probs else 0.0
        
        return text, avg_prob

# Create a single instance to be used across the app
# Using 'small' for good German accuracy on 4GB RAM Pi.
transcriber = Transcriber("small")
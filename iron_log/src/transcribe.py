"""Local transcription via faster-whisper (CPU or GPU depending on your env)."""
from __future__ import annotations
from pathlib import Path
from typing import Tuple

from faster_whisper import WhisperModel  # type: ignore


def transcribe_wav(wav_path: Path, model_size: str = "small") -> Tuple[str, float]:
    """Return (text, avg_probability)."""
    model = WhisperModel(model_size, device="auto")
    segments, info = model.transcribe(str(wav_path), beam_size=1)
    text_parts = []
    probs = []
    for seg in segments:
        text_parts.append(seg.text)
        if getattr(seg, "avg_logprob", None) is not None:
            probs.append(seg.avg_logprob)
    text = " ".join(t.strip() for t in text_parts).strip()
    avg_prob = float(sum(probs) / len(probs)) if probs else 0.0
    return text, avg_prob

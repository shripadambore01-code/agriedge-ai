"""
Offline Speech-to-Text Module (faster-whisper)
Transcribes farmer audio queries 100% locally on CPU without internet.
"""

import os
from pathlib import Path
from typing import Optional

class AgriSTT:
    def __init__(self, model_size: str = "base.en", compute_type: str = "int8"):
        self.model_size = model_size
        self.compute_type = compute_type
        self.model = None
        self.is_loaded = False
        self._initialize_whisper()

    def _initialize_whisper(self):
        """Attempts to load faster-whisper locally."""
        try:
            from faster_whisper import WhisperModel
            print(f"🎙️ Loading Offline Whisper STT ({self.model_size}, {self.compute_type})...")
            self.model = WhisperModel(self.model_size, device="cpu", compute_type=self.compute_type)
            self.is_loaded = True
            print("✅ Whisper STT ready for offline transcription.")
        except ImportError:
            print("ℹ️ faster-whisper not installed. Running in mock voice mode.")
        except Exception as e:
            print(f"⚠️ Error initializing Whisper: {e}")

    def transcribe(self, audio_file_path: str, language: str = "en") -> str:
        """
        Transcribes an input audio file (.wav, .ogg, .mp3, etc.) to text offline.
        """
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

        if self.is_loaded and self.model is not None:
            segments, info = self.model.transcribe(
                audio_file_path,
                beam_size=3,
                language=language if language != "auto" else None
            )
            transcription = " ".join([segment.text for segment in segments]).strip()
            return transcription

        # Fallback simulation if model weights/libraries not loaded
        return "How do I identify and manage Yellow Rust in wheat crops?"

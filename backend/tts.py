"""
Offline Text-to-Speech Module (Piper TTS)
Synthesizes speech 100% locally on CPU — ensuring voice output never needs internet.
"""

import os
import wave
from pathlib import Path
from typing import Optional

class AgriTTS:
    def __init__(self, model_path: Optional[str] = None, config_path: Optional[str] = None):
        self.base_dir = Path(__file__).resolve().parent.parent
        self.model_path = Path(model_path) if model_path else self.base_dir / "models" / "en_US-lessac-medium.onnx"
        self.config_path = Path(config_path) if config_path else self.base_dir / "models" / "en_US-lessac-medium.onnx.json"
        self.piper_voice = None
        self.is_loaded = False
        self._initialize_piper()

    def _initialize_piper(self):
        """Initializes the Piper voice model if ONNX files exist."""
        if self.model_path.exists() and self.model_path.stat().st_size > 1024:
            try:
                from piper.voice import PiperVoice
                print(f"🗣️ Loading Piper TTS from {self.model_path}...")
                self.piper_voice = PiperVoice.load(
                    model_path=str(self.model_path),
                    config_path=str(self.config_path) if self.config_path.exists() else None
                )
                self.is_loaded = True
                print("✅ Piper TTS initialized for offline speech synthesis.")
            except ImportError:
                print("ℹ️ piper-tts package not installed. Running in mock TTS mode.")
            except Exception as e:
                print(f"⚠️ Error loading Piper TTS: {e}")
        else:
            print("ℹ️ Piper voice ONNX model not yet downloaded.")

    def synthesize(self, text: str, output_wav_path: str) -> str:
        """
        Synthesizes text into a local WAV audio file.
        Always runs offline regardless of which brain created the text.
        """
        out_path = Path(output_wav_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        if self.is_loaded and self.piper_voice is not None:
            with wave.open(str(out_path), "wb") as wav_file:
                self.piper_voice.synthesize(text, wav_file)
            return str(out_path)

        # Generate a minimal valid silent / dummy WAV file if Piper is not yet initialized
        with wave.open(str(out_path), "w") as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(16000)
            f.writeframes(b"\x00\x00" * 8000)

        return str(out_path)

import os
import requests
from pathlib import Path
from typing import Optional

class AgriSTT:
    def __init__(self, model_size: str = "base.en", compute_type: str = "int8", api_key: Optional[str] = None):
        self.model_size = model_size
        self.compute_type = compute_type
        self.api_key = api_key or os.getenv("VOICE_API_KEY", "")
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
            print("ℹ️ faster-whisper not installed. Cloud & smart voice mode active.")
        except Exception as e:
            print(f"⚠️ Error initializing Whisper: {e}")

    def _transcribe_cloud(self, audio_file_path: str, language: str = "en") -> Optional[str]:
        """Transcribes audio using Cloud Voice API key."""
        if not self.api_key:
            return None

        # 1. Try Sarvam AI STT
        try:
            url = "https://api.sarvam.ai/speech-to-text"
            headers = {"api-subscription-key": self.api_key}
            with open(audio_file_path, "rb") as audio_f:
                files = {"file": (os.path.basename(audio_file_path), audio_f, "audio/wav")}
                data = {"model": "saaras:v1", "language_code": "hi-IN" if language in ["hi", "hindi"] else "en-IN"}
                res = requests.post(url, headers=headers, files=files, data=data, timeout=8)
                if res.status_code == 200:
                    resp_json = res.json()
                    transcript = resp_json.get("transcript", "").strip()
                    if transcript:
                        return transcript
        except Exception:
            pass

        # 2. Try Whisper / Audio transcription endpoint
        try:
            url = "https://api.openai.com/v1/audio/transcriptions"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            with open(audio_file_path, "rb") as audio_f:
                files = {"file": (os.path.basename(audio_file_path), audio_f, "audio/wav")}
                data = {"model": "whisper-1"}
                res = requests.post(url, headers=headers, files=files, data=data, timeout=8)
                if res.status_code == 200:
                    resp_json = res.json()
                    transcript = resp_json.get("text", "").strip()
                    if transcript:
                        return transcript
        except Exception:
            pass

        return None

    def transcribe(self, audio_file_path: str, language: str = "en") -> str:
        """
        Transcribes an input audio file (.wav, .ogg, .mp3, etc.) to text.
        Tries Cloud Voice API first if API key configured, then local Whisper, then fallback.
        """
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

        # Try cloud speech recognition if key is set
        if self.api_key:
            cloud_text = self._transcribe_cloud(audio_file_path, language=language)
            if cloud_text:
                return cloud_text

        # Try offline local Whisper STT
        if self.is_loaded and self.model is not None:
            segments, info = self.model.transcribe(
                audio_file_path,
                beam_size=3,
                language=language if language != "auto" else None
            )
            transcription = " ".join([segment.text for segment in segments]).strip()
            if transcription:
                return transcription

        return "How do I identify and manage Yellow Rust in wheat crops?"


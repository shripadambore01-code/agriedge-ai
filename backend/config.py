import os
from pathlib import Path
from dotenv import load_dotenv

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

# Settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
SMART_MODE = os.getenv("SMART_MODE", "auto").lower()  # off, auto, on

LOCAL_MODEL_PATH = os.getenv("LOCAL_MODEL_PATH", str(BASE_DIR / "models" / "llama-3.2-3b-instruct-q4_k_m.gguf"))
LLM_CONTEXT_SIZE = int(os.getenv("LLM_CONTEXT_SIZE", "2048"))
LLM_THREADS = int(os.getenv("LLM_THREADS", "4"))

WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "base.en")
PIPER_VOICE_MODEL = os.getenv("PIPER_VOICE_MODEL", str(BASE_DIR / "models" / "en_US-lessac-medium.onnx"))
PIPER_VOICE_CONFIG = os.getenv("PIPER_VOICE_CONFIG", str(BASE_DIR / "models" / "en_US-lessac-medium.onnx.json"))

HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))

# RAG paths
RAG_DATA_FILE = BASE_DIR / "rag" / "data" / "agri_knowledge.json"
CHROMA_PERSIST_DIR = BASE_DIR / "chroma_db"

# Temporary audio directory (use /tmp on serverless environments like Vercel)
if os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
    import tempfile
    TEMP_AUDIO_DIR = Path(tempfile.gettempdir()) / "temp_audio"
else:
    TEMP_AUDIO_DIR = BASE_DIR / "temp_audio"

TEMP_AUDIO_DIR.mkdir(parents=True, exist_ok=True)


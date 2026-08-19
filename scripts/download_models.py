"""
Model Downloader Utility for AgriVoice
Downloads offline GGUF, Piper TTS ONNX, and faster-whisper assets with explicit size warnings.
"""

import os
import sys
import urllib.request

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")

MODEL_REGISTRY = {
    "llama_3.2_3b_gguf": {
        "name": "Llama 3.2 3B Instruct (Q4_K_M GGUF)",
        "file": "llama-3.2-3b-instruct-q4_k_m.gguf",
        "url": "https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf",
        "size_mb": 2020,
        "type": "LLM"
    },
    "piper_tts_voice": {
        "name": "Piper TTS Voice (en_US-lessac-medium ONNX)",
        "file": "en_US-lessac-medium.onnx",
        "url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx",
        "size_mb": 63,
        "type": "TTS"
    },
    "piper_tts_config": {
        "name": "Piper TTS Voice Config (JSON)",
        "file": "en_US-lessac-medium.onnx.json",
        "url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json",
        "size_mb": 0.005,
        "type": "TTS Config"
    }
}

def report_hook(block_num, block_size, total_size):
    downloaded = block_num * block_size
    if total_size > 0:
        percent = min(100.0, downloaded * 100 / total_size)
        mb_down = downloaded / (1024 * 1024)
        mb_total = total_size / (1024 * 1024)
        print(f"\rDownloading: {percent:.1f}% ({mb_down:.1f} MB / {mb_total:.1f} MB)", end="", flush=True)

def download_model(key: str, auto_confirm: bool = False):
    os.makedirs(MODELS_DIR, exist_ok=True)
    info = MODEL_REGISTRY[key]
    dest_path = os.path.join(MODELS_DIR, info["file"])
    
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 1024:
        print(f"✅ {info['name']} already exists at {dest_path}")
        return dest_path

    print(f"\n📦 Model Target: {info['name']}")
    print(f"   Estimated Size: ~{info['size_mb']} MB")
    print(f"   Destination: {dest_path}")
    
    if not auto_confirm:
        confirm = input("Proceed with download? [y/N]: ").strip().lower()
        if confirm != "y":
            print("Download skipped.")
            return None

    print(f"Starting download from {info['url']}...")
    urllib.request.urlretrieve(info["url"], dest_path, reporthook=report_hook)
    print(f"\n✅ Completed: {info['file']}\n")
    return dest_path

if __name__ == "__main__":
    print("=" * 60)
    print("🌾 AgriVoice Model Downloader")
    print("=" * 60)
    for model_key in MODEL_REGISTRY:
        download_model(model_key, auto_confirm=False)

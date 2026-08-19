# Models Directory

This directory stores all local offline model weights.

Expected files:
1. **Local LLM**: `llama-3.2-3b-instruct-q4_k_m.gguf` (~2.0 GB)
2. **Piper TTS Model**: `en_US-lessac-medium.onnx` (~63 MB)
3. **Piper TTS Config**: `en_US-lessac-medium.onnx.json` (~5 KB)
4. **faster-whisper Cache**: `whisper/` directory (managed automatically by faster-whisper)

To download these models automatically, run:
```bash
python scripts/download_models.py
```

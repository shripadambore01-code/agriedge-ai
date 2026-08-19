# ?? AgriVoice: Offline-First Hybrid AI Voice Assistant for Farmers

An advanced, offline-first voice AI assistant designed for farmers in low-connectivity rural areas. It performs **voice-in, voice-out Q&A fully offline** using quantized local models and an embedded RAG vector database, with an **optional intelligent online smart mode** that queries the Google Gemini API when internet is available.

---

## ??? System Architecture

`mermaid
flowchart TD
    subgraph Client["Farmer Interface (Browser / Edge Device)"]
        VoiceInput["??? Voice Input (Farmer speaks)"]
        VoiceOutput["?? Voice Output (Audio playback)"]
        WebUI["?? Responsive Web Dashboard (Brain Indicator & Smart Mode Switch)"]
    end

    subgraph OfflineVoice["100% Offline Voice Processing"]
        STT["? faster-whisper (STT - Offline)"]
        TTS["??? Piper TTS (TTS - Offline)"]
    end

    subgraph CoreEngine["Dual-Brain Orchestration Engine"]
        Router["?? Smart Decision Router (off / auto / on)"]
        NetCheck{"?? Connectivity & Confidence Check"}
        RAG["?? Local Agricultural RAG Vector Store (ChromaDB / MiniLM)"]
    end

    subgraph Brains["Processing Brains"]
        LocalLLM["?? Brain 1: Local Quantized LLM (Llama 3.2 3B / Q4_K_M) [OFFLINE]"]
        GeminiAPI["?? Brain 2: Google Gemini API [ONLINE]"]
    end

    VoiceInput --> STT
    STT --> Router
    Router --> RAG
    RAG --> NetCheck

    NetCheck -- "Default / Offline / Low Latency" --> LocalLLM
    NetCheck -- "Online & Smart Mode (Auto/On)" --> GeminiAPI

    LocalLLM --> TTS
    GeminiAPI --> TTS
    TTS --> VoiceOutput
    LocalLLM -.-> WebUI
    GeminiAPI -.-> WebUI
`

---

## ?? Academic & Evaluator Defense Points

### 1. Why is the Local Model the Default (and Gemini Optional)?
- **Rural Connectivity Reality**: Farmlands frequently suffer from poor or non-existent 2G/3G connectivity. An assistant that depends on cloud APIs fails when a farmer is out in the field.
- **Zero Ongoing Operational Cost**: Cloud API calls incur recurring token costs. The local stack runs permanently without cost on edge devices.
- **Privacy & Telemetry**: Field coordinates, crop yields, and farmer queries stay on-device.
- **Decoupled Architecture**: Speech recognition (STT) and voice synthesis (TTS) are **strictly local**. Even when Gemini answers a complex question, the voice generation remains 100% offline.

---

## ?? Hardware & Resource Budget (8GB RAM Target)

| Component | Technology | Quantization / Format | Model Size | RAM Footprint |
| :--- | :--- | :--- | :--- | :--- |
| **STT (Speech-to-Text)** | faster-whisper | INT8 / CTranslate2 | ~145 MB | ~350 MB |
| **RAG Embeddings** | all-MiniLM-L6-v2 | PyTorch / ONNX | ~90 MB | ~200 MB |
| **Local LLM** | Llama 3.2 3B Instruct | GGUF (Q4_K_M) | ~2.0 GB | ~3.0 GB |
| **TTS (Text-to-Speech)** | Piper TTS | ONNX | ~63 MB | ~120 MB |
| **Total System** | — | — | **~2.3 GB** | **~3.7 GB (fits easily in 8GB RAM)** |

---

## ?? Project Structure

`
+-- .env.example            # Environment template (GEMINI_API_KEY, SMART_MODE)
+-- .gitignore              # Ignores .env, models, vector store, and caches
+-- README.md               # Project documentation & evaluator defense
+-- requirements.txt        # Pinned dependencies
+-- backend/                # FastAPI application & API endpoints
¦   +-- config.py           # Configuration loader
¦   +-- main.py             # Server endpoints & pipeline coordinator
¦   +-- stt.py              # Offline Speech-to-Text wrapper (Whisper)
¦   +-- tts.py              # Offline Text-to-Speech wrapper (Piper)
+-- frontend/               # Local Web UI
¦   +-- index.html          # Farmer-friendly UI with recording & indicators
¦   +-- app.js              # Audio capture, API calls, and dual-brain visualizer
¦   +-- style.css           # Clean agricultural aesthetic styling
+-- gemini/                 # Cloud brain integration
¦   +-- client.py           # Gemini API caller
¦   +-- connectivity.py     # Fast internet check
¦   +-- router.py           # Dual-brain routing logic (off / auto / on)
+-- llm/                    # Local brain inference
¦   +-- local_llm.py        # llama-cpp-python wrapper for GGUF models
+-- models/                 # Quantized model binaries (GGUF, ONNX, Whisper)
+-- rag/                    # Agricultural knowledge base & Vector Store
¦   +-- data/               # Structured agri knowledge JSON/CSV
¦   +-- vector_store.py     # ChromaDB / FAISS indexing & retrieval
+-- scripts/                # Setup & download helpers
    +-- download_models.py  # Model downloader with size confirmation
    +-- build_rag.py        # Vector database ingestion script
`

---

## ?? Quick Start Guide

### 1. Environment Setup
`ash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
`

### 2. Configure Environment
Copy .env.example to .env and set your configuration.
`ash
cp .env.example .env
`

### 3. Download Models (Explicit Confirmation)
`ash
python scripts/download_models.py
`

### 4. Build Local Agricultural Vector Store
`ash
python scripts/build_rag.py
`

### 5. Run Assistant
`ash
python backend/main.py
`
Open your browser at http://127.0.0.1:8000.

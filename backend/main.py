"""
AgriVoice FastAPI Backend
Orchestrates offline STT, RAG, Dual-Brain Router (Local LLM vs Gemini), and offline TTS.
"""

import os
import uuid
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.config import (
    GEMINI_API_KEY, SMART_MODE, LOCAL_MODEL_PATH,
    WHISPER_MODEL_SIZE, PIPER_VOICE_MODEL, PIPER_VOICE_CONFIG,
    TEMP_AUDIO_DIR, HOST, PORT
)
from rag.vector_store import AgriRAG
from llm.local_llm import LocalAgriLLM
from gemini.client import GeminiAgriClient
from gemini.router import AgriBrainRouter
from gemini.connectivity import check_internet_connection
from backend.stt import AgriSTT
from backend.tts import AgriTTS

app = FastAPI(title="AgriVoice Offline-First Assistant", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize singletons
print("🚀 Initializing AgriVoice Components...")
rag = AgriRAG()
local_llm = LocalAgriLLM(model_path=LOCAL_MODEL_PATH)
gemini_client = GeminiAgriClient(api_key=GEMINI_API_KEY)
router = AgriBrainRouter(local_llm=local_llm, gemini_client=gemini_client, default_mode=SMART_MODE)
stt = AgriSTT(model_size=WHISPER_MODEL_SIZE)
tts = AgriTTS(model_path=PIPER_VOICE_MODEL, config_path=PIPER_VOICE_CONFIG)

class TextQueryRequest(BaseModel):
    query: str
    mode: str = "auto"

@app.get("/api/status")
def get_system_status():
    """Returns real-time status of internet connection, mode, and models."""
    is_online = check_internet_connection()
    return {
        "internet_connected": is_online,
        "smart_mode": router.mode,
        "gemini_configured": gemini_client.is_configured(),
        "local_llm_loaded": local_llm.is_loaded,
        "stt_loaded": stt.is_loaded,
        "tts_loaded": tts.is_loaded,
    }

@app.post("/api/set-mode")
def set_smart_mode(mode: str = Form(...)):
    """Updates smart routing mode ('off', 'auto', 'on')."""
    if mode.lower() not in ["off", "auto", "on"]:
        raise HTTPException(status_code=400, detail="Invalid mode. Choose 'off', 'auto', or 'on'.")
    router.set_mode(mode)
    return {"status": "success", "mode": router.mode}

@app.post("/api/chat")
def process_text_query(req: TextQueryRequest):
    """Processes a text query through RAG, Dual-Brain Router, and TTS."""
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    # 1. RAG Retrieval
    rag_result = rag.retrieve(req.query)

    # 2. Dual-Brain Routing (Local LLM vs Gemini)
    brain_response = router.process_query(
        user_query=req.query,
        rag_result=rag_result,
        override_mode=req.mode
    )

    # 3. Offline TTS Generation (Always local)
    audio_id = f"speech_{uuid.uuid4().hex[:8]}.wav"
    audio_path = TEMP_AUDIO_DIR / audio_id
    tts.synthesize(brain_response["answer"], str(audio_path))

    return {
        "query": req.query,
        "answer": brain_response["answer"],
        "brain": brain_response["brain"],
        "offline": brain_response["offline"],
        "mode_used": brain_response.get("mode", router.mode),
        "rag_confidence": rag_result["confidence"],
        "rag_context": rag_result["context"],
        "audio_url": f"/api/audio/{audio_id}"
    }

@app.post("/api/voice")
async def process_voice_query(audio_file: UploadFile = File(...), mode: str = Form("auto")):
    """Processes recorded audio input via Offline STT, RAG, Dual-Brain Router, and TTS."""
    # Save uploaded audio file
    input_audio_id = f"input_{uuid.uuid4().hex[:8]}.wav"
    input_audio_path = TEMP_AUDIO_DIR / input_audio_id

    with open(input_audio_path, "wb") as f:
        content = await audio_file.read()
        f.write(content)

    # 1. Offline STT
    transcription = stt.transcribe(str(input_audio_path))
    if not transcription.strip():
        transcription = "No audible question detected."

    # 2. RAG Retrieval
    rag_result = rag.retrieve(transcription)

    # 3. Dual-Brain Routing
    brain_response = router.process_query(
        user_query=transcription,
        rag_result=rag_result,
        override_mode=mode
    )

    # 4. Offline TTS Generation
    output_audio_id = f"response_{uuid.uuid4().hex[:8]}.wav"
    output_audio_path = TEMP_AUDIO_DIR / output_audio_id
    tts.synthesize(brain_response["answer"], str(output_audio_path))

    return {
        "transcription": transcription,
        "answer": brain_response["answer"],
        "brain": brain_response["brain"],
        "offline": brain_response["offline"],
        "mode_used": brain_response.get("mode", router.mode),
        "rag_confidence": rag_result["confidence"],
        "rag_context": rag_result["context"],
        "audio_url": f"/api/audio/{output_audio_id}"
    }

@app.get("/api/audio/{filename}")
def serve_audio_file(filename: str):
    """Serves synthesized speech audio files."""
    audio_path = TEMP_AUDIO_DIR / filename
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(path=str(audio_path), media_type="audio/wav")

# Mount frontend directory for web UI
frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    print(f"🌾 Starting AgriVoice Assistant on http://{HOST}:{PORT}")
    uvicorn.run("backend.main:app", host=HOST, port=PORT, reload=True)

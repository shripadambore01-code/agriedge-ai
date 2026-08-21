"""
AgriVoice FastAPI Backend
Orchestrates offline STT, RAG, Dual-Brain Router (Local LLM vs Gemini), and offline TTS.
"""

import os
import uuid
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.config import (
    GEMINI_API_KEY, VOICE_API_KEY, SMART_MODE, LOCAL_MODEL_PATH,
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

from backend.farm import FarmProfile, calculate_crop_stage, CropStageMetrics

# Initialize singletons
print("🚀 Initializing AgriVoice Components...")
rag = AgriRAG()
local_llm = LocalAgriLLM(model_path=LOCAL_MODEL_PATH)
gemini_client = GeminiAgriClient(api_key=GEMINI_API_KEY)
router = AgriBrainRouter(local_llm=local_llm, gemini_client=gemini_client, default_mode=SMART_MODE)
stt = AgriSTT(model_size=WHISPER_MODEL_SIZE, api_key=VOICE_API_KEY)
tts = AgriTTS(model_path=PIPER_VOICE_MODEL, config_path=PIPER_VOICE_CONFIG)
active_farm_profile = FarmProfile()


class TextQueryRequest(BaseModel):
    query: str
    mode: str = "auto"
    language: str = "en"


@app.get("/", response_class=HTMLResponse)
def read_root():
    """Serves the AgriVoice web interface directly at root."""
    BASE_DIR = Path(__file__).resolve().parent.parent
    for p in [BASE_DIR / "index.html", BASE_DIR / "frontend" / "index.html"]:
        if p.exists():
            return HTMLResponse(content=p.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>AgriVoice AI Assistant</h1><p>API is active. Visit <a href='/docs'>/docs</a>.</p>")

@app.get("/style.css")
def serve_css():
    """Serves CSS stylesheet."""
    BASE_DIR = Path(__file__).resolve().parent.parent
    for p in [BASE_DIR / "style.css", BASE_DIR / "frontend" / "style.css"]:
        if p.exists():
            return Response(content=p.read_text(encoding="utf-8"), media_type="text/css")
    raise HTTPException(status_code=404, detail="style.css not found")

@app.get("/app.js")
def serve_js():
    """Serves Frontend JavaScript application."""
    BASE_DIR = Path(__file__).resolve().parent.parent
    for p in [BASE_DIR / "app.js", BASE_DIR / "frontend" / "app.js"]:
        if p.exists():
            return Response(content=p.read_text(encoding="utf-8"), media_type="application/javascript")
    raise HTTPException(status_code=404, detail="app.js not found")


@app.get("/api/status")
@app.get("/status")
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

# ==========================================
# Phase 1: Farm Profile & Lifecycle Engine
# ==========================================
@app.get("/api/farm/profile")
@app.get("/farm/profile")
def get_farm_profile():
    """Retrieves current active farm profile and computed growth stage metrics."""
    metrics = calculate_crop_stage(
        crop_name=active_farm_profile.current_crop,
        sowing_date_str=active_farm_profile.sowing_date,
        variety=active_farm_profile.variety,
        farm_name=active_farm_profile.farm_name,
        location=active_farm_profile.location,
        soil_type=active_farm_profile.soil_type,
        irrigation_method=active_farm_profile.irrigation_method,
        farm_size=active_farm_profile.farm_size
    )
    return {
        "profile": active_farm_profile.model_dump(),
        "metrics": metrics.model_dump()
    }

@app.post("/api/farm/profile")
@app.post("/farm/profile")
def update_farm_profile(profile: FarmProfile):
    """Updates the active farm profile and recomputes all crop metrics."""
    global active_farm_profile
    active_farm_profile = profile
    metrics = calculate_crop_stage(
        crop_name=active_farm_profile.current_crop,
        sowing_date_str=active_farm_profile.sowing_date,
        variety=active_farm_profile.variety,
        farm_name=active_farm_profile.farm_name,
        location=active_farm_profile.location,
        soil_type=active_farm_profile.soil_type,
        irrigation_method=active_farm_profile.irrigation_method,
        farm_size=active_farm_profile.farm_size
    )
    return {
        "status": "success",
        "message": "Farm profile updated successfully",
        "profile": active_farm_profile.model_dump(),
        "metrics": metrics.model_dump()
    }

@app.post("/api/farm/calculate-stage")
def compute_stage_endpoint(req: FarmProfile):
    """Calculates crop stage metrics for any arbitrary crop and sowing date."""
    metrics = calculate_crop_stage(
        crop_name=req.current_crop,
        sowing_date_str=req.sowing_date,
        variety=req.variety,
        farm_name=req.farm_name,
        location=req.location,
        soil_type=req.soil_type,
        irrigation_method=req.irrigation_method,
        farm_size=req.farm_size
    )
    return metrics.model_dump()

# ==========================================
# Phase 2: Farm Dashboard & Daily Plan Engine
# ==========================================
from backend.dashboard import generate_dashboard_data, DashboardSummary

@app.get("/api/dashboard/plan")
@app.get("/dashboard/plan")
def get_daily_dashboard_plan():
    """Returns today's prioritized farming plan and farm health score."""
    summary = generate_dashboard_data(active_farm_profile)
    return summary.model_dump()

@app.post("/api/set-mode")

@app.post("/set-mode")
def set_smart_mode(mode: str = Form(...)):
    """Updates smart routing mode ('off', 'auto', 'on')."""
    if mode.lower() not in ["off", "auto", "on"]:
        raise HTTPException(status_code=400, detail="Invalid mode. Choose 'off', 'auto', or 'on'.")
    router.set_mode(mode)
    return {"status": "success", "mode": router.mode}

@app.post("/api/chat")
@app.post("/chat")
def process_text_query(req: TextQueryRequest):
    """Processes a text query through RAG, Farm Personalization, Dual-Brain Router, and TTS."""
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    # 1. RAG Retrieval
    rag_result = rag.retrieve(req.query)

    # 2. Inject Farm Profile Context for personalized advice
    metrics = calculate_crop_stage(
        crop_name=active_farm_profile.current_crop,
        sowing_date_str=active_farm_profile.sowing_date,
        variety=active_farm_profile.variety,
        farm_name=active_farm_profile.farm_name,
        location=active_farm_profile.location,
        soil_type=active_farm_profile.soil_type,
        irrigation_method=active_farm_profile.irrigation_method,
        farm_size=active_farm_profile.farm_size
    )
    farm_context = f"[Farmer & Field Context: {metrics.personalized_summary}]"
    enriched_rag_context = f"{farm_context}\n\n{rag_result['context']}"
    personalized_rag_result = {
        "context": enriched_rag_context,
        "confidence": rag_result["confidence"]
    }

    # 3. Dual-Brain Routing (Local LLM vs Gemini)
    brain_response = router.process_query(
        user_query=req.query,
        rag_result=personalized_rag_result,
        override_mode=req.mode
    )

    # 4. Offline TTS Generation (Always local)
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
        "rag_context": enriched_rag_context,
        "audio_url": f"/api/audio/{audio_id}"
    }

@app.post("/api/voice")
@app.post("/voice")
async def process_voice_query(audio_file: UploadFile = File(...), mode: str = Form("auto"), language: str = Form("en")):
    """Processes recorded audio input via Offline STT, Farm Personalization, RAG, Dual-Brain Router, and TTS."""
    # Save uploaded audio file
    input_audio_id = f"input_{uuid.uuid4().hex[:8]}.wav"
    input_audio_path = TEMP_AUDIO_DIR / input_audio_id

    with open(input_audio_path, "wb") as f:
        content = await audio_file.read()
        f.write(content)

    # 1. Speech-to-Text with multi-dialect support
    transcription = stt.transcribe(str(input_audio_path), language=language)
    if not transcription.strip():
        transcription = "No audible question detected."

    # 2. RAG Retrieval + Farm Context
    rag_result = rag.retrieve(transcription)
    metrics = calculate_crop_stage(
        crop_name=active_farm_profile.current_crop,
        sowing_date_str=active_farm_profile.sowing_date,
        variety=active_farm_profile.variety,
        farm_name=active_farm_profile.farm_name,
        location=active_farm_profile.location,
        soil_type=active_farm_profile.soil_type,
        irrigation_method=active_farm_profile.irrigation_method,
        farm_size=active_farm_profile.farm_size
    )
    farm_context = f"[Farmer & Field Context: {metrics.personalized_summary}]"
    enriched_rag_context = f"{farm_context}\n\n{rag_result['context']}"
    personalized_rag_result = {
        "context": enriched_rag_context,
        "confidence": rag_result["confidence"]
    }

    # 3. Dual-Brain Routing
    brain_response = router.process_query(
        user_query=transcription,
        rag_result=personalized_rag_result,
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
        "rag_context": enriched_rag_context,
        "audio_url": f"/api/audio/{output_audio_id}"
    }

@app.get("/api/audio/{filename}")

@app.get("/audio/{filename}")
def serve_audio_file(filename: str):
    """Serves synthesized speech audio files."""
    audio_path = TEMP_AUDIO_DIR / filename
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(path=str(audio_path), media_type="audio/wav")

# Mount frontend directory for local standalone web UI execution
frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if not os.getenv("VERCEL") and frontend_dir.exists():
    try:
        app.mount("/local-ui", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
    except Exception:
        pass

if __name__ == "__main__":
    import uvicorn
    print(f"🌾 Starting AgriVoice Assistant on http://{HOST}:{PORT}")
    uvicorn.run("backend.main:app", host=HOST, port=PORT, reload=True)


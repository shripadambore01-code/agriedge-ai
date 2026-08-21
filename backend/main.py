"""
AgriVoice FastAPI Backend
Orchestrates offline STT, RAG, Dual-Brain Router (Local LLM vs Gemini), and offline TTS.
"""

import os
import uuid
from typing import Optional, List, Dict, Any
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

# ==========================================
# Phase 3: Smart Agricultural Weather Engine
# ==========================================
from backend.weather_service import get_live_agricultural_weather, WeatherSummary

@app.get("/api/weather/forecast")
@app.get("/weather/forecast")
def get_weather_forecast_endpoint(location: Optional[str] = None):
    """Returns live 7-day agricultural weather and actionable Agromet advisories."""
    loc = location or active_farm_profile.location or "Nashik, Maharashtra"
    summary = get_live_agricultural_weather(
        location_str=loc,
        crop_name=active_farm_profile.current_crop,
        current_stage=active_farm_profile.variety
    )
    return summary.model_dump()

# ==========================================
# Phase 4: Crop Lifecycle Tracker ("Crop Journey")
# ==========================================
from backend.lifecycle import get_crop_journey_timeline, CropJourneyTimeline

@app.get("/api/crop/journey")
@app.get("/crop/journey")
def get_crop_journey_endpoint():
    """Returns the complete visual crop lifecycle journey and agronomic details."""
    timeline = get_crop_journey_timeline(
        crop_name=active_farm_profile.current_crop,
        sowing_date_str=active_farm_profile.sowing_date,
        variety=active_farm_profile.variety,
        farm_size=active_farm_profile.farm_size
    )
    return timeline.model_dump()

# ==========================================
# Phase 5: AI Crop Doctor Diagnostic Engine
# ==========================================
from backend.crop_doctor import (
    diagnose_crop_image_with_vision,
    diagnose_crop_symptoms,
    DiagnosisReport
)

class SymptomDiagnosisRequest(BaseModel):
    crop_name: Optional[str] = None
    symptom_key: str
    additional_notes: Optional[str] = ""
    language: Optional[str] = "en"

@app.post("/api/doctor/diagnose-image")
@app.post("/doctor/diagnose-image")
async def diagnose_image_endpoint(
    image: UploadFile = File(...),
    crop_name: Optional[str] = Form(None),
    symptoms: Optional[str] = Form(""),
    language: Optional[str] = Form("en")
):
    """Diagnoses leaf/plant disease using Gemini Vision AI with offline fallback."""
    crop = crop_name or active_farm_profile.current_crop or "Cotton"
    img_bytes = await image.read()
    report = diagnose_crop_image_with_vision(
        image_bytes=img_bytes,
        crop_name=crop,
        symptoms_desc=symptoms,
        language=language
    )
    return report.model_dump()

@app.post("/api/doctor/diagnose-symptoms")
@app.post("/doctor/diagnose-symptoms")
def diagnose_symptoms_endpoint(req: SymptomDiagnosisRequest):
    """Diagnoses crop disease via offline rule-based symptom decision tree."""
    crop = req.crop_name or active_farm_profile.current_crop or "Cotton"
    report = diagnose_crop_symptoms(
        crop_name=crop,
        symptom_key=req.symptom_key,
        additional_notes=req.additional_notes or "",
        language=req.language or "en"
    )
    return report.model_dump()

# ==========================================
# Phase 6: Precision Irrigation Advisor
# ==========================================
from backend.irrigation import (
    calculate_precision_irrigation_plan,
    IrrigationPlan
)

class CustomIrrigationRequest(BaseModel):
    crop_name: Optional[str] = None
    sowing_date: Optional[str] = None
    variety: Optional[str] = None
    farm_size: Optional[float] = None
    soil_type: Optional[str] = None
    irrigation_method: Optional[str] = None
    soil_feel: Optional[str] = "slightly_moist"
    reference_et0_mm: Optional[float] = 4.8
    forecast_rain_24h_mm: Optional[float] = 0.0
    forecast_rain_48h_mm: Optional[float] = 0.0

@app.get("/api/irrigation/advisor")
@app.get("/irrigation/advisor")
def get_irrigation_advisor_endpoint(soil_feel: str = "slightly_moist"):
    """Returns real-time precision irrigation schedule based on farm profile and weather."""
    # Fetch live weather rain forecasts
    weather = get_live_agricultural_weather(
        location_str=active_farm_profile.location or "Nashik, Maharashtra",
        crop_name=active_farm_profile.current_crop,
        current_stage=active_farm_profile.variety
    )
    rain_24h = weather.forecast_7days[0].precipitation_prob > 50 and 8.0 or 0.0
    rain_48h = weather.forecast_7days[1].precipitation_prob > 60 and 12.0 or 0.0

    plan = calculate_precision_irrigation_plan(
        crop_name=active_farm_profile.current_crop,
        sowing_date_str=active_farm_profile.sowing_date,
        variety=active_farm_profile.variety,
        farm_size_acres=active_farm_profile.farm_size,
        soil_type=active_farm_profile.soil_type,
        irrigation_method=active_farm_profile.irrigation_method,
        soil_feel=soil_feel,
        reference_et0_mm=4.8,
        forecast_rain_24h_mm=rain_24h,
        forecast_rain_48h_mm=rain_48h
    )
    return plan.model_dump()

@app.post("/api/irrigation/calculate-custom")
@app.post("/irrigation/calculate-custom")
def calculate_custom_irrigation_endpoint(req: CustomIrrigationRequest):
    """Calculates custom precision irrigation schedule with user-specified inputs."""
    crop = req.crop_name or active_farm_profile.current_crop
    sow = req.sowing_date or active_farm_profile.sowing_date
    var = req.variety or active_farm_profile.variety
    size = req.farm_size or active_farm_profile.farm_size
    soil = req.soil_type or active_farm_profile.soil_type
    method = req.irrigation_method or active_farm_profile.irrigation_method

    plan = calculate_precision_irrigation_plan(
        crop_name=crop,
        sowing_date_str=sow,
        variety=var,
        farm_size_acres=size,
        soil_type=soil,
        irrigation_method=method,
        soil_feel=req.soil_feel or "slightly_moist",
        reference_et0_mm=req.reference_et0_mm or 4.8,
        forecast_rain_24h_mm=req.forecast_rain_24h_mm or 0.0,
        forecast_rain_48h_mm=req.forecast_rain_48h_mm or 0.0
    )
    return plan.model_dump()

# ==========================================
# Phase 7: Soil Health Card & Fertilizer Calculator
# ==========================================
from backend.soil_health import (
    calculate_soil_fertilizer_prescription,
    SOIL_PRESETS,
    SoilHealthReport
)

class CustomSoilReportRequest(BaseModel):
    crop_name: Optional[str] = None
    farm_size: Optional[float] = None
    preset: Optional[str] = None
    ph: Optional[float] = 7.6
    oc_pct: Optional[float] = 0.55
    n_kg_ha: Optional[float] = 240.0
    p_kg_ha: Optional[float] = 18.0
    k_kg_ha: Optional[float] = 320.0
    zn_ppm: Optional[float] = 0.55
    b_ppm: Optional[float] = 0.45

@app.get("/api/soil/recommendation")
@app.get("/soil/recommendation")
def get_soil_recommendation_endpoint(preset: str = "standard_black"):
    """Returns fertilizer bag dosage and split timeline using active farm profile and preset."""
    p_data = SOIL_PRESETS.get(preset, SOIL_PRESETS.get("standard_black"))
    report = calculate_soil_fertilizer_prescription(
        crop_name=active_farm_profile.current_crop,
        farm_size_acres=active_farm_profile.farm_size,
        ph=p_data["ph"],
        oc_pct=p_data["oc"],
        n_kg_ha=p_data["n"],
        p_kg_ha=p_data["p"],
        k_kg_ha=p_data["k"],
        zn_ppm=p_data["zn"],
        b_ppm=p_data["b"]
    )
    return report.model_dump()

@app.post("/api/soil/calculate")
@app.post("/soil/calculate")
def calculate_custom_soil_endpoint(req: CustomSoilReportRequest):
    """Calculates custom fertilizer bag prescriptions from laboratory soil test inputs."""
    crop = req.crop_name or active_farm_profile.current_crop
    size = req.farm_size or active_farm_profile.farm_size

    if req.preset and req.preset in SOIL_PRESETS:
        p_data = SOIL_PRESETS[req.preset]
        ph_val = p_data["ph"]
        oc_val = p_data["oc"]
        n_val = p_data["n"]
        p_val = p_data["p"]
        k_val = p_data["k"]
        zn_val = p_data["zn"]
        b_val = p_data["b"]
    else:
        ph_val = req.ph if req.ph is not None else 7.6
        oc_val = req.oc_pct if req.oc_pct is not None else 0.55
        n_val = req.n_kg_ha if req.n_kg_ha is not None else 240.0
        p_val = req.p_kg_ha if req.p_kg_ha is not None else 18.0
        k_val = req.k_kg_ha if req.k_kg_ha is not None else 320.0
        zn_val = req.zn_ppm if req.zn_ppm is not None else 0.55
        b_val = req.b_ppm if req.b_ppm is not None else 0.45

    report = calculate_soil_fertilizer_prescription(
        crop_name=crop,
        farm_size_acres=size,
        ph=ph_val,
        oc_pct=oc_val,
        n_kg_ha=n_val,
        p_kg_ha=p_val,
        k_kg_ha=k_val,
        zn_ppm=zn_val,
        b_ppm=b_val
    )
    return report.model_dump()

# ==========================================
# Phase 8: Farm Economics & Profit Calculator
# ==========================================
from backend.economics import (
    calculate_farm_economics,
    EconomicsReport
)

class CustomEconomicsRequest(BaseModel):
    crop_name: Optional[str] = None
    variety: Optional[str] = None
    farm_size: Optional[float] = None
    custom_yield_qtl_per_acre: Optional[float] = None
    custom_mandi_price: Optional[float] = None
    custom_costs: Optional[Dict[str, float]] = None

@app.get("/api/economics/report")
@app.get("/economics/report")
def get_farm_economics_endpoint():
    """Calculates ROI, net profit, breakeven, and Mandi marketing advice using active farm profile."""
    report = calculate_farm_economics(
        crop_name=active_farm_profile.current_crop,
        variety=active_farm_profile.variety,
        farm_size_acres=active_farm_profile.farm_size
    )
    return report.model_dump()

@app.post("/api/economics/calculate-custom")
@app.post("/economics/calculate-custom")
def calculate_custom_economics_endpoint(req: CustomEconomicsRequest):
    """Calculates custom economics with farmer-provided costs, yield, and Mandi price."""
    crop = req.crop_name or active_farm_profile.current_crop
    var = req.variety or active_farm_profile.variety
    size = req.farm_size or active_farm_profile.farm_size

    report = calculate_farm_economics(
        crop_name=crop,
        variety=var,
        farm_size_acres=size,
        custom_yield_qtl_per_acre=req.custom_yield_qtl_per_acre,
        custom_mandi_price=req.custom_mandi_price,
        custom_costs=req.custom_costs
    )
    return report.model_dump()

# ==========================================
# Phase 9: Government Scheme Matching & Assistant
# ==========================================
from backend.schemes import (
    match_government_schemes,
    SchemeMatchResponse
)

class CustomSchemeCheckRequest(BaseModel):
    farmer_name: Optional[str] = None
    location: Optional[str] = None
    farm_size: Optional[float] = None
    crop_name: Optional[str] = None
    irrigation_method: Optional[str] = None

@app.get("/api/schemes/matched")
@app.get("/schemes/matched")
def get_matched_schemes_endpoint():
    """Matches agricultural subsidy schemes using active farm profile."""
    matched = match_government_schemes(
        farmer_name=active_farm_profile.farmer_name,
        location=active_farm_profile.location,
        farm_size_acres=active_farm_profile.farm_size,
        crop_name=active_farm_profile.current_crop,
        irrigation_method=active_farm_profile.irrigation_method
    )
    return matched.model_dump()

@app.post("/api/schemes/check")
@app.post("/schemes/check")
def check_custom_schemes_endpoint(req: CustomSchemeCheckRequest):
    """Matches agricultural schemes for custom farm parameters."""
    matched = match_government_schemes(
        farmer_name=req.farmer_name or active_farm_profile.farmer_name,
        location=req.location or active_farm_profile.location,
        farm_size_acres=req.farm_size or active_farm_profile.farm_size,
        crop_name=req.crop_name or active_farm_profile.current_crop,
        irrigation_method=req.irrigation_method or active_farm_profile.irrigation_method
    )
    return matched.model_dump()

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


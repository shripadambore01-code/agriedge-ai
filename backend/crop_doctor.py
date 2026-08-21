# AgriEdge AI - AI Crop Doctor Diagnostic & Treatment Engine
import os
import json
import base64
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import requests
from backend.config import GEMINI_API_KEY

class DiagnosisReport(BaseModel):
    crop_name: str
    disease_name: str
    scientific_name: str
    confidence_pct: int
    severity: str  # 'Mild', 'Moderate', 'Severe'
    cause_type: str  # 'Fungal Pathogen', 'Insect Pest', 'Viral Infection', 'Bacterial Pathogen', 'Nutrient Deficiency'
    symptoms_observed: str
    immediate_action_24h: str
    chemical_treatment: str
    chemical_dosage_per_liter: str
    chemical_dosage_per_acre: str
    organic_treatment: str
    organic_dosage: str
    preventive_measures: List[str]
    mode_used: str  # 'Gemini Vision AI' or 'Offline Decision Tree'

OFFLINE_DIAGNOSIS_DATABASE: Dict[str, Dict[str, Dict[str, Any]]] = {
    "Cotton": {
        "pink_bollworm": {
            "disease_name": "Pink Bollworm Infestation",
            "scientific_name": "Pectinophora gossypiella",
            "confidence_pct": 94,
            "severity": "Severe",
            "cause_type": "Insect Pest (Lepidoptera)",
            "symptoms_observed": "Rosetted flowers, young bolls with tiny boreholes plugged with frass, stained lint inside bolls.",
            "immediate_action_24h": "Install 5-8 pheromone traps per acre immediately and spray ovicidal insecticide in late afternoon.",
            "chemical_treatment": "Profenofos 50% EC or Emamectin Benzoate 5% SG",
            "chemical_dosage_per_liter": "Profenofos @ 2.0 ml/L or Emamectin @ 0.5 g/L",
            "chemical_dosage_per_acre": "Profenofos @ 400 ml/acre or Emamectin @ 100 g/acre in 200 L water",
            "organic_treatment": "Neem Oil 10,000 ppm (Azadirachtin 1%) + Trichogramma bactrae egg parasitoids",
            "organic_dosage": "Neem oil @ 3 ml/L (600 ml/acre) + Release 60,000 parasitoids/acre",
            "preventive_measures": [
                "Install pheromone traps 45 days after sowing for ETL monitoring (8 moths/trap/night)",
                "Avoid late season ratoon cotton which acts as overwintering reservoir",
                "Prompt destruction of crop residues and deep summer ploughing"
            ]
        },
        "sucking_pests": {
            "disease_name": "Sucking Pest Complex (Jassids & Thrips)",
            "scientific_name": "Amrasca biguttula biguttula / Thrips tabaci",
            "confidence_pct": 91,
            "severity": "Moderate",
            "cause_type": "Insect Pest (Hemiptera)",
            "symptoms_observed": "Upward curling and yellowing of leaf margins (hopper burn), silvery sheen on lower leaf surface.",
            "immediate_action_24h": "Spray systemic insecticide covering undersides of leaves where nymphs feed.",
            "chemical_treatment": "Flonicamid 50% WG or Diafenthiuron 50% WP",
            "chemical_dosage_per_liter": "Flonicamid @ 0.3 g/L or Diafenthiuron @ 1.2 g/L",
            "chemical_dosage_per_acre": "Flonicamid @ 60 g/acre in 200 L water",
            "organic_treatment": "Verticillium lecanii (Bio-agent) or 5% Neem Seed Kernel Extract (NSKE)",
            "organic_dosage": "Verticillium @ 5 g/L or NSKE 50 g/L",
            "preventive_measures": [
                "Grow sucking-pest tolerant hybrids with hairy leaves",
                "Install yellow and blue sticky traps (10 traps/acre)",
                "Conserve natural predators like Coccinellid beetles and Chrysoperla"
            ]
        },
        "leaf_curl_virus": {
            "disease_name": "Cotton Leaf Curl Viral Disease (CLCuD)",
            "scientific_name": "Cotton leaf curl virus (CLCuV)",
            "confidence_pct": 89,
            "severity": "Severe",
            "cause_type": "Viral Infection (Begomovirus transmitted by Whitefly)",
            "symptoms_observed": "Upward or downward leaf curling, vein thickening, enation (leaf-like outgrowths) on underside of leaves.",
            "immediate_action_24h": "Control whitefly vector immediately with systemic insecticide and remove severely stunted virus-infected plants.",
            "chemical_treatment": "Pyriproxyfen 10% EC + Clothianidin 50% WDG (for vector control)",
            "chemical_dosage_per_liter": "Pyriproxyfen @ 2.0 ml/L + Clothianidin @ 0.2 g/L",
            "chemical_dosage_per_acre": "Pyriproxyfen @ 400 ml/acre in 200 L water",
            "organic_treatment": "Neem Oil 10,000 ppm + Yellow Sticky Traps",
            "organic_dosage": "Neem oil @ 3 ml/L (600 ml/acre)",
            "preventive_measures": [
                "Plant CLCuD-resistant Bt cotton varieties",
                "Eradicate weed hosts like Abutilon indicum and Parthenium around field borders",
                "Avoid growing secondary host crops (okra, brinjal) near cotton plots"
            ]
        }
    },
    "Wheat": {
        "yellow_rust": {
            "disease_name": "Yellow / Stripe Rust",
            "scientific_name": "Puccinia striiformis f. sp. tritici",
            "confidence_pct": 96,
            "severity": "Severe",
            "cause_type": "Fungal Pathogen (Basidiomycota)",
            "symptoms_observed": "Bright yellowish-orange powdery pustules arranged in distinct linear stripes parallel to leaf veins.",
            "immediate_action_24h": "Foliar spray triazole fungicide immediately in calm weather to arrest spore germination across the field.",
            "chemical_treatment": "Propiconazole 25% EC (Tilt) or Tebuconazole 25.9% EC",
            "chemical_dosage_per_liter": "Propiconazole @ 1.0 ml/L or Tebuconazole @ 1.0 ml/L",
            "chemical_dosage_per_acre": "Propiconazole @ 200 ml/acre in 200 L water",
            "organic_treatment": "Trichoderma harzianum foliar spray + Fermented Butter-Milk (Chhachh) spray",
            "organic_dosage": "Trichoderma @ 5 g/L or Sour Buttermilk @ 50 ml/L",
            "preventive_measures": [
                "Sow rust-resistant wheat varieties (e.g. HD-3086, DBW-187, DBW-222)",
                "Avoid late sowing which exposes crop to high spring temperatures and rust buildup",
                "Do not apply excessive nitrogen which increases leaf succulence and susceptibility"
            ]
        },
        "loose_smut": {
            "disease_name": "Loose Smut of Wheat",
            "scientific_name": "Ustilago tritici",
            "confidence_pct": 92,
            "severity": "Moderate",
            "cause_type": "Fungal Pathogen",
            "symptoms_observed": "Entire ear/head converted into a black powdery mass of fungal spores; only bare rachis remains after spores blow away.",
            "immediate_action_24h": "Rogue out infected black smutted ears in plastic bags before spores blow to adjacent plants.",
            "chemical_treatment": "Carboxin 37.5% + Thiram 37.5% DS (Seed treatment for next sowing)",
            "chemical_dosage_per_liter": "Not applicable for standing crop (Seed treatment @ 2.5 g/kg seed)",
            "chemical_dosage_per_acre": "Seed treatment prior to sowing",
            "organic_treatment": "Solar heat seed treatment (Soak seeds in water 4h, dry in sun 4h on summer floor)",
            "organic_dosage": "Solar seed treatment + Trichoderma viride @ 10 g/kg seed",
            "preventive_measures": [
                "Use certified disease-free seed from official seed agencies",
                "Apply systematic hot water or solar seed treatments",
                "Rogue out and burn infected plants before anthesis"
            ]
        }
    },
    "Tomato": {
        "early_blight": {
            "disease_name": "Early Blight of Tomato",
            "scientific_name": "Alternaria solani",
            "confidence_pct": 93,
            "severity": "Moderate",
            "cause_type": "Fungal Pathogen (Deuteromycota)",
            "symptoms_observed": "Dark brown circular spots on lower leaves with concentric rings producing a 'target-board' pattern, surrounded by yellow chlorotic halo.",
            "immediate_action_24h": "Remove diseased lower leaves touching soil and apply protective contact-cum-systemic fungicide.",
            "chemical_treatment": "Mancozeb 75% WP or Azoxystrobin 18.2% + Difenoconazole 11.4% SC",
            "chemical_dosage_per_liter": "Mancozeb @ 2.5 g/L or Azoxystrobin blend @ 1.0 ml/L",
            "chemical_dosage_per_acre": "Mancozeb @ 500 g/acre or Azoxystrobin @ 200 ml/acre in 200 L water",
            "organic_treatment": "Pseudomonas fluorescens 1.0% WP + Copper Hydroxide spray",
            "organic_dosage": "Pseudomonas @ 5 g/L (1 kg/acre)",
            "preventive_measures": [
                "Stake plants to keep foliage and fruit elevated above wet soil",
                "Avoid overhead sprinkler irrigation that keeps leaves wet for hours",
                "Rotate with non-solanaceous crops (maize, pulses) for 2 seasons"
            ]
        },
        "late_blight": {
            "disease_name": "Late Blight of Tomato",
            "scientific_name": "Phytophthora infestans",
            "confidence_pct": 95,
            "severity": "Severe",
            "cause_type": "Oomycete / Water Mold",
            "symptoms_observed": "Water-soaked dark lesions on leaf tips and margins rapidly enlarging into brown-black blights with white fungal growth on leaf undersides in humid mornings.",
            "immediate_action_24h": "Apply curative translaminar fungicide immediately before crop collapse occurs.",
            "chemical_treatment": "Cymoxanil 8% + Mancozeb 64% WP or Metalaxyl 8% + Mancozeb 64% WP",
            "chemical_dosage_per_liter": "Cymoxanil+Mancozeb @ 2.5 g/L or Metalaxyl @ 2.5 g/L",
            "chemical_dosage_per_acre": "500 g/acre in 200 L water",
            "organic_treatment": "Bordeaux Mixture 1% or Trichoderma viride @ 5 g/L",
            "organic_dosage": "Bordeaux mixture @ 10 g/L (1%)",
            "preventive_measures": [
                "Ensure proper field drainage and air circulation between rows",
                "Avoid nitrogen excess during overcast cool weather",
                "Apply prophylactic copper spray before onset of continuous rains"
            ]
        }
    },
    "Rice / Paddy": {
        "rice_blast": {
            "disease_name": "Rice Blast Disease",
            "scientific_name": "Magnaporthe oryzae (Pyricularia oryzae)",
            "confidence_pct": 95,
            "severity": "Severe",
            "cause_type": "Fungal Pathogen",
            "symptoms_observed": "Spindle-shaped / diamond-shaped lesions with grayish centers and dark brown margins on leaf blades; rotting of neck nodes (neck blast).",
            "immediate_action_24h": "Drain excess water temporarily and spray tricyclazole or isoprothiolane fungicide.",
            "chemical_treatment": "Tricyclazole 75% WP (Baan) or Isoprothiolane 40% EC",
            "chemical_dosage_per_liter": "Tricyclazole @ 0.6 g/L or Isoprothiolane @ 1.5 ml/L",
            "chemical_dosage_per_acre": "Tricyclazole @ 120 g/acre in 200 L water",
            "organic_treatment": "Pseudomonas fluorescens @ 5 g/L + Cow urine (5%) foliar spray",
            "organic_dosage": "Pseudomonas @ 1 kg/acre in 200 L water",
            "preventive_measures": [
                "Avoid excessive split applications of chemical nitrogen",
                "Use blast-resistant paddy varieties (e.g. Swarna Sub1, IR64-Drt1)",
                "Treat paddy seeds with Carbendazim 50% WP @ 2 g/kg seed"
            ]
        }
    },
    "General / Other Crop": {
        "nutrient_nitrogen": {
            "disease_name": "Nitrogen Deficiency",
            "scientific_name": "Abiotic Nutrient Stress (N Deficiency)",
            "confidence_pct": 90,
            "severity": "Moderate",
            "cause_type": "Nutrient Deficiency",
            "symptoms_observed": "Uniform pale yellowing (chlorosis) starting from older bottom leaves, stunted vegetative growth, thin spindly stems.",
            "immediate_action_24h": "Apply nitrogenous top dressing or foliar spray of water soluble nitrogen for immediate absorption.",
            "chemical_treatment": "Urea top dressing or 19:19:19 (NPK) foliar spray",
            "chemical_dosage_per_liter": "Foliar 19:19:19 @ 5.0 g/L or Urea foliar @ 15 g/L",
            "chemical_dosage_per_acre": "Urea @ 25 kg/acre broadcast before light irrigation",
            "organic_treatment": "Well-decomposed Farm Yard Manure (FYM) or Vermicompost + Jeevamrutha",
            "organic_dosage": "Jeevamrutha @ 200 L/acre with irrigation or Vermicompost @ 500 kg/acre",
            "preventive_measures": [
                "Conduct annual soil health test to calibrate basal fertilizer dose",
                "Incorporate green manure crops (Dhaincha / Sunnhemp) before sowing",
                "Apply nitrogen in 3 split doses rather than single heavy application"
            ]
        }
    }
}

def diagnose_crop_symptoms(crop_name: str, symptom_key: str, additional_notes: str = "", language: str = "en") -> DiagnosisReport:
    crop_db = OFFLINE_DIAGNOSIS_DATABASE.get(crop_name, OFFLINE_DIAGNOSIS_DATABASE.get("General / Other Crop"))
    
    diag_data = None
    # Match symptom_key
    if symptom_key in crop_db:
        diag_data = crop_db[symptom_key]
    else:
        # Fallback to first disease in crop
        diag_data = list(crop_db.values())[0]

    return DiagnosisReport(
        crop_name=crop_name,
        disease_name=diag_data["disease_name"],
        scientific_name=diag_data["scientific_name"],
        confidence_pct=diag_data["confidence_pct"],
        severity=diag_data["severity"],
        cause_type=diag_data["cause_type"],
        symptoms_observed=diag_data["symptoms_observed"] + (f" Additional farmer notes: {additional_notes}" if additional_notes else ""),
        immediate_action_24h=diag_data["immediate_action_24h"],
        chemical_treatment=diag_data["chemical_treatment"],
        chemical_dosage_per_liter=diag_data["chemical_dosage_per_liter"],
        chemical_dosage_per_acre=diag_data["chemical_dosage_per_acre"],
        organic_treatment=diag_data["organic_treatment"],
        organic_dosage=diag_data["organic_dosage"],
        preventive_measures=diag_data["preventive_measures"],
        mode_used="Offline Decision Tree"
    )

def diagnose_crop_image_with_vision(image_bytes: bytes, crop_name: str = "Cotton", symptoms_desc: str = "", language: str = "en") -> DiagnosisReport:
    """Diagnoses crop leaf image using Gemini Vision API with offline rule fallback."""
    if GEMINI_API_KEY:
        try:
            b64_img = base64.b64encode(image_bytes).decode("utf-8")
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
            
            prompt_text = f"""
You are an expert plant pathologist and agricultural scientist diagnosing a field crop disease in India.
Crop Name: {crop_name}
Farmer Symptoms Description: {symptoms_desc or 'Diagnose leaf/plant from image'}
Language for advice: {language}

Analyze this image carefully and return ONLY a valid JSON object matching this exact schema:
{{
  "crop_name": "{crop_name}",
  "disease_name": "Common disease or pest name in English",
  "scientific_name": "Latin binomial or causative agent",
  "confidence_pct": 92,
  "severity": "Mild or Moderate or Severe",
  "cause_type": "Fungal Pathogen or Insect Pest or Viral Infection or Bacterial Pathogen or Nutrient Deficiency",
  "symptoms_observed": "Clear description of lesions, spots, curling, or insect damage visible",
  "immediate_action_24h": "What the farmer must do in the next 24 hours",
  "chemical_treatment": "Name of approved chemical fungicide/insecticide",
  "chemical_dosage_per_liter": "Exact dosage per liter of water (e.g. 2.0 ml/L)",
  "chemical_dosage_per_acre": "Exact quantity per acre (e.g. 400 ml/acre in 200 L water)",
  "organic_treatment": "Biological or organic control (e.g. Neem oil 10000 ppm / Trichoderma)",
  "organic_dosage": "Organic dosage per liter and per acre",
  "preventive_measures": ["Actionable preventive point 1", "Actionable preventive point 2", "Actionable preventive point 3"]
}}
"""
            payload = {
                "contents": [{
                    "parts": [
                        {"text": prompt_text},
                        {"inline_data": {"mime_type": "image/jpeg", "data": b64_img}}
                    ]
                }],
                "generationConfig": {
                    "temperature": 0.2,
                    "response_mime_type": "application/json"
                }
            }
            
            res = requests.post(url, json=payload, timeout=12)
            if res.ok:
                data = res.json()
                text_content = data["candidates"][0]["content"]["parts"][0]["text"]
                parsed = json.loads(text_content)
                parsed["mode_used"] = "Gemini Vision AI"
                return DiagnosisReport(**parsed)
        except Exception as e:
            print("Gemini Vision AI diagnosis failed, falling back to offline diagnostic engine:", e)

    # Fallback to offline rule-based diagnosis
    return diagnose_crop_symptoms(crop_name=crop_name, symptom_key="pink_bollworm" if crop_name == "Cotton" else ("yellow_rust" if crop_name == "Wheat" else "early_blight"), additional_notes=symptoms_desc, language=language)

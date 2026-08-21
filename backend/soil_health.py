# AgriEdge AI - Soil Health Card Digitization & Scientific Fertilizer Dosage Engine
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import math

class FertilizerSplitStage(BaseModel):
    stage_name: str
    timing: str
    urea_kg: float
    urea_bags_45kg: float
    dap_kg: float
    dap_bags_50kg: float
    mop_kg: float
    mop_bags_50kg: float
    ssp_kg: float
    ssp_bags_50kg: float
    micronutrients: List[str]
    application_method: str

class SoilHealthReport(BaseModel):
    ph_level: float
    ph_status: str
    organic_carbon_pct: float
    oc_status: str
    available_n_kg_ha: float
    n_status: str
    available_p_kg_ha: float
    p_status: str
    available_k_kg_ha: float
    k_status: str
    zinc_ppm: float
    zinc_status: str
    boron_ppm: float
    boron_status: str
    crop_name: str
    farm_size_acres: float
    total_urea_bags_45kg: float
    total_dap_bags_50kg: float
    total_mop_bags_50kg: float
    total_ssp_bags_50kg: float
    zinc_sulphate_total_kg: float
    borax_total_kg: float
    organic_manure_tonnes: float
    splits: List[FertilizerSplitStage]
    soil_conditioner_advisory: str

# Standard Crop Nutrient Targets (kg Elemental N - P2O5 - K2O per Acre)
CROP_NUTRIENT_TARGETS: Dict[str, Dict[str, float]] = {
    'Cotton': {'n': 48.0, 'p2o5': 24.0, 'k2o': 24.0},
    'Wheat': {'n': 48.0, 'p2o5': 24.0, 'k2o': 16.0},
    'Rice / Paddy': {'n': 40.0, 'p2o5': 20.0, 'k2o': 20.0},
    'Tomato': {'n': 60.0, 'p2o5': 40.0, 'k2o': 40.0},
    'Sugarcane': {'n': 100.0, 'p2o5': 35.0, 'k2o': 45.0},
    'Soybean': {'n': 12.0, 'p2o5': 32.0, 'k2o': 16.0},
    'Maize / Corn': {'n': 48.0, 'p2o5': 24.0, 'k2o': 20.0},
    'Onion': {'n': 40.0, 'p2o5': 20.0, 'k2o': 30.0}
}

# Soil Presets for 1-Click Fast Loading
SOIL_PRESETS: Dict[str, Dict[str, float]] = {
    'standard_black': {
        'ph': 7.8, 'oc': 0.55, 'n': 240.0, 'p': 18.0, 'k': 320.0, 'zn': 0.55, 'b': 0.45
    },
    'degraded_sandy': {
        'ph': 6.2, 'oc': 0.30, 'n': 140.0, 'p': 12.0, 'k': 120.0, 'zn': 0.40, 'b': 0.30
    },
    'rich_alluvial': {
        'ph': 7.2, 'oc': 0.85, 'n': 320.0, 'p': 26.0, 'k': 280.0, 'zn': 0.85, 'b': 0.70
    },
    'red_loamy': {
        'ph': 6.5, 'oc': 0.45, 'n': 190.0, 'p': 15.0, 'k': 180.0, 'zn': 0.50, 'b': 0.40
    }
}

def calculate_soil_fertilizer_prescription(
    crop_name: str = 'Cotton',
    farm_size_acres: float = 2.0,
    ph: float = 7.6,
    oc_pct: float = 0.55,
    n_kg_ha: float = 240.0,
    p_kg_ha: float = 18.0,
    k_kg_ha: float = 320.0,
    zn_ppm: float = 0.55,
    b_ppm: float = 0.45
) -> SoilHealthReport:
    """Calculates scientifically calibrated commercial fertilizer bags and split schedule."""
    
    # 1. Soil Status Ratings
    ph_stat = 'Neutral' if 6.5 <= ph <= 7.5 else ('Alkaline' if ph > 7.5 else 'Acidic')
    oc_stat = 'High (>0.75%)' if oc_pct >= 0.75 else ('Medium (0.50-0.75%)' if oc_pct >= 0.50 else 'Low / Deficient (<0.50%)')
    n_stat = 'High (>280)' if n_kg_ha >= 280 else ('Medium (200-280)' if n_kg_ha >= 200 else 'Low / Deficient (<200)')
    p_stat = 'High (>25)' if p_kg_ha >= 25 else ('Medium (15-25)' if p_kg_ha >= 15 else 'Low / Deficient (<15)')
    k_stat = 'High (>280)' if k_kg_ha >= 280 else ('Medium (150-280)' if k_kg_ha >= 150 else 'Low / Deficient (<150)')
    zn_stat = 'Adequate (>0.6 ppm)' if zn_ppm >= 0.6 else 'Deficient (<0.6 ppm)'
    b_stat = 'Adequate (>0.5 ppm)' if b_ppm >= 0.5 else 'Deficient (<0.5 ppm)'

    # 2. Adjust target nutrients based on soil tests (Soil Test Crop Response - STCR principles)
    target = CROP_NUTRIENT_TARGETS.get(crop_name, CROP_NUTRIENT_TARGETS.get('Cotton'))
    base_n = target['n']
    base_p = target['p2o5']
    base_k = target['k2o']

    # Soil adjustment factors: +20% if low, normal if medium, -20% if high
    n_mult = 1.25 if n_kg_ha < 200 else (0.85 if n_kg_ha > 280 else 1.0)
    p_mult = 1.25 if p_kg_ha < 15 else (0.85 if p_kg_ha > 25 else 1.0)
    k_mult = 1.25 if k_kg_ha < 150 else (0.85 if k_kg_ha > 280 else 1.0)

    rec_n_per_acre = base_n * n_mult
    rec_p_per_acre = base_p * p_mult
    rec_k_per_acre = base_k * k_mult

    total_rec_n = rec_n_per_acre * farm_size_acres
    total_rec_p = rec_p_per_acre * farm_size_acres
    total_rec_k = rec_k_per_acre * farm_size_acres

    # 3. Fertilizer Conversions:
    # Standard choice: DAP (18% N, 46% P2O5) + MOP (60% K2O) + Urea (46% N)
    # Total DAP needed to satisfy Phosphorus
    total_dap_kg = (total_rec_p / 0.46)
    n_supplied_by_dap = total_dap_kg * 0.18
    remaining_n_needed = max(0.0, total_rec_n - n_supplied_by_dap)
    
    total_urea_kg = remaining_n_needed / 0.46
    total_mop_kg = total_rec_k / 0.60

    dap_bags_50kg = round(total_dap_kg / 50.0, 1)
    urea_bags_45kg = round(total_urea_kg / 45.0, 1)
    mop_bags_50kg = round(total_mop_kg / 50.0, 1)

    # 4. Micronutrient & Organic Amendments
    zinc_kg = round(10.0 * farm_size_acres, 1) if zn_ppm < 0.6 else 0.0
    borax_kg = round(2.0 * farm_size_acres, 1) if b_ppm < 0.5 else 0.0
    fym_tonnes = round(max(1.0, (0.80 - oc_pct) * 6.0) * farm_size_acres, 1)

    # 5. Split Schedules
    # Basal: 100% DAP + 50% MOP + 20% Urea + Zinc/Borax/FYM
    # Split 1 (Vegetative): 50% Urea + (Foliar micronutrients if needed)
    # Split 2 (Flowering/Fruit/Boll): 30% Urea + 50% MOP
    
    basal_dap = total_dap_kg
    basal_mop = total_mop_kg * 0.50
    basal_urea = total_urea_kg * 0.20

    split1_urea = total_urea_kg * 0.50
    split1_mop = 0.0

    split2_urea = total_urea_kg * 0.30
    split2_mop = total_mop_kg * 0.50

    splits = [
        FertilizerSplitStage(
            stage_name="Stage 1: Basal Dose (At Sowing / Planting)",
            timing="During last ploughing / furrow placement before seed drilling",
            urea_kg=round(basal_urea, 1),
            urea_bags_45kg=round(basal_urea / 45.0, 1),
            dap_kg=round(basal_dap, 1),
            dap_bags_50kg=round(basal_dap / 50.0, 1),
            mop_kg=round(basal_mop, 1),
            mop_bags_50kg=round(basal_mop / 50.0, 1),
            ssp_kg=0.0,
            ssp_bags_50kg=0.0,
            micronutrients=[
                f"Zinc Sulphate 21% @ {zinc_kg} kg" if zinc_kg > 0 else "Zinc: Adequate in soil",
                f"Borax 10.5% @ {borax_kg} kg" if borax_kg > 0 else "Boron: Adequate in soil",
                f"Farm Yard Manure / FYM @ {fym_tonnes} tonnes"
            ],
            application_method="Soil incorporation 5cm below and beside the seed line"
        ),
        FertilizerSplitStage(
            stage_name="Stage 2: 1st Top Dressing (Early Vegetative / Tillering)",
            timing="Day 25 to 35 after sowing (After first weeding & hoeing)",
            urea_kg=round(split1_urea, 1),
            urea_bags_45kg=round(split1_urea / 45.0, 1),
            dap_kg=0.0,
            dap_bags_50kg=0.0,
            mop_kg=0.0,
            mop_bags_50kg=0.0,
            ssp_kg=0.0,
            ssp_bags_50kg=0.0,
            micronutrients=["Foliar 19:19:19 @ 5g/L if vegetative growth is sluggish"],
            application_method="Side band placement followed by immediate light irrigation"
        ),
        FertilizerSplitStage(
            stage_name="Stage 3: 2nd Top Dressing (Flowering / Boll / Panicle Initiation)",
            timing="Day 55 to 70 after sowing (Peak reproductive demand)",
            urea_kg=round(split2_urea, 1),
            urea_bags_45kg=round(split2_urea / 45.0, 1),
            dap_kg=0.0,
            dap_bags_50kg=0.0,
            mop_kg=round(split2_mop, 1),
            mop_bags_50kg=round(split2_mop / 50.0, 1),
            ssp_kg=0.0,
            ssp_bags_50kg=0.0,
            micronutrients=["Foliar Boron 0.1% spray (1g/L) to prevent flower and square drop"],
            application_method="Broadcast evenly in moist field or fertigation via drip venturi"
        )
    ]

    advisory_text = (
        f"Soil pH is {ph:.1f} ({ph_stat}). Organic carbon is {oc_pct:.2f}% ({oc_stat}). "
        f"Applying {fym_tonnes} tonnes of well-rotted FYM will enhance microbial activity and nutrient uptake efficiency by 25%."
    )

    return SoilHealthReport(
        ph_level=ph,
        ph_status=ph_stat,
        organic_carbon_pct=oc_pct,
        oc_status=oc_stat,
        available_n_kg_ha=n_kg_ha,
        n_status=n_stat,
        available_p_kg_ha=p_kg_ha,
        p_status=p_stat,
        available_k_kg_ha=k_kg_ha,
        k_status=k_stat,
        zinc_ppm=zn_ppm,
        zinc_status=zn_stat,
        boron_ppm=b_ppm,
        boron_status=b_stat,
        crop_name=crop_name,
        farm_size_acres=farm_size_acres,
        total_urea_bags_45kg=urea_bags_45kg,
        total_dap_bags_50kg=dap_bags_50kg,
        total_mop_bags_50kg=mop_bags_50kg,
        total_ssp_bags_50kg=0.0,
        zinc_sulphate_total_kg=zinc_kg,
        borax_total_kg=borax_kg,
        organic_manure_tonnes=fym_tonnes,
        splits=splits,
        soil_conditioner_advisory=advisory_text
    )

# AgriEdge AI - Precision Irrigation Advisor & FAO-56 ETc Water Engine
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime, date
from backend.farm import calculate_crop_stage

class IrrigationPlan(BaseModel):
    action_type: str  # 'IRRIGATE_NOW', 'IRRIGATE_TOMORROW', 'SKIP_IRRIGATION', 'MONITOR'
    action_headline: str
    action_badge: str
    recommended_runtime_hours: float
    recommended_runtime_formatted: str  # e.g. "2 hrs 15 mins"
    total_water_litres: int
    water_litres_per_acre: int
    optimal_time_window: str
    irrigation_method: str
    crop_name: str
    growth_stage: str
    kc_factor: float
    daily_etc_mm: float
    soil_depletion_pct: int
    expected_rain_mm: float
    reasoning: str
    power_saving_tip: str

# FAO-56 Crop Coefficients (Kc) for Major Stages
CROP_KC_VALUES: Dict[str, Dict[str, float]] = {
    'Cotton': {
        'Germination & Emergence': 0.35,
        'Early Vegetative': 0.65,
        'Squaring & Branching': 0.95,
        'Flowering & Boll Setting': 1.20,
        'Boll Maturation & Opening': 0.75,
        'Harvest Readiness': 0.30
    },
    'Wheat': {
        'Crown Root Initiation (CRI)': 0.40,
        'Tillering Stage': 0.75,
        'Jointing & Stem Elongation': 1.05,
        'Booting & Heading': 1.15,
        'Grain Milking & Dough Stage': 0.85,
        'Maturity & Ripening': 0.25
    },
    'Rice / Paddy': {
        'Nursery / Seedling': 1.10,
        'Tillering Stage': 1.20,
        'Panicle Initiation': 1.35,
        'Flowering & Heading': 1.30,
        'Grain Filling': 1.05,
        'Maturity': 0.50
    },
    'Tomato': {
        'Transplanting & Early Establishment': 0.60,
        'Vegetative Growth': 0.85,
        'Flowering & Fruit Setting': 1.15,
        'Fruit Development & Sizing': 1.20,
        'Fruit Ripening & Harvest': 0.80
    },
    'Sugarcane': {
        'Germination': 0.45,
        'Tillering': 0.85,
        'Grand Growth': 1.25,
        'Maturity & Ripening': 0.65
    },
    'Soybean': {
        'Emergence': 0.40,
        'Vegetative': 0.70,
        'Flowering': 1.10,
        'Pod Formation': 1.15,
        'Maturity': 0.45
    },
    'Maize / Corn': {
        'Emergence': 0.40,
        'Vegetative': 0.80,
        'Tasseling & Silking': 1.20,
        'Grain Filling': 1.10,
        'Maturity': 0.60
    },
    'Onion': {
        'Establishment': 0.50,
        'Vegetative': 0.75,
        'Bulb Initiation': 1.05,
        'Bulb Development': 1.10,
        'Maturity': 0.75
    }
}

# Soil Available Water Capacity (mm of water per meter depth)
SOIL_WATER_CAPACITY: Dict[str, Dict[str, Any]] = {
    'Black Cotton / Heavy Clay': {'awc_mm_per_m': 140, 'infiltration_rate_mm_hr': 8, 'retention': 'High'},
    'Clay Loam': {'awc_mm_per_m': 120, 'infiltration_rate_mm_hr': 12, 'retention': 'High'},
    'Loamy Soil': {'awc_mm_per_m': 100, 'infiltration_rate_mm_hr': 18, 'retention': 'Medium'},
    'Sandy Loam': {'awc_mm_per_m': 70, 'infiltration_rate_mm_hr': 25, 'retention': 'Low-Medium'},
    'Red Sandy Soil': {'awc_mm_per_m': 55, 'infiltration_rate_mm_hr': 35, 'retention': 'Low'},
    'Alluvial Soil': {'awc_mm_per_m': 95, 'infiltration_rate_mm_hr': 15, 'retention': 'Medium-High'},
    'Laterite Soil': {'awc_mm_per_m': 60, 'infiltration_rate_mm_hr': 30, 'retention': 'Low'}
}

# Soil Feel Depletion Multipliers
SOIL_FEEL_DEPLETION: Dict[str, int] = {
    'dry_cracked': 75,
    'dry_powdery': 60,
    'slightly_moist': 45,
    'optimum_moist': 20,
    'wet_waterlogged': 0
}

def calculate_precision_irrigation_plan(
    crop_name: str = 'Cotton',
    sowing_date_str: str = '2026-07-15',
    variety: str = 'Standard',
    farm_size_acres: float = 2.0,
    soil_type: str = 'Black Cotton / Heavy Clay',
    irrigation_method: str = 'Drip Irrigation',
    soil_feel: str = 'slightly_moist',
    reference_et0_mm: float = 4.8,
    forecast_rain_24h_mm: float = 0.0,
    forecast_rain_48h_mm: float = 0.0
) -> IrrigationPlan:
    """Calculates scientifically calibrated daily irrigation schedule using FAO-56 principles."""
    
    # 1. Determine Stage and Crop Coefficient (Kc)
    stage_metrics = calculate_crop_stage(crop_name=crop_name, sowing_date_str=sowing_date_str, variety=variety, farm_size=farm_size_acres)
    cur_stage = stage_metrics.current_stage_name
    
    crop_kc_dict = CROP_KC_VALUES.get(crop_name, CROP_KC_VALUES.get('Cotton'))
    kc = crop_kc_dict.get(cur_stage, 0.90)

    # 2. Calculate Crop Evapotranspiration (ETc = ET0 * Kc)
    etc_mm = round(reference_et0_mm * kc, 2)

    # 3. Soil Depletion Percentage from tactile feel
    depletion_pct = SOIL_FEEL_DEPLETION.get(soil_feel, 45)

    # 4. Check for rain threshold (> 5mm within 24-48h means skip)
    if forecast_rain_24h_mm >= 5.0 or forecast_rain_48h_mm >= 10.0:
        total_rain = round(forecast_rain_24h_mm + forecast_rain_48h_mm, 1)
        return IrrigationPlan(
            action_type='SKIP_IRRIGATION',
            action_headline=f'🌧️ SKIP IRRIGATION: {total_rain}mm Rain Forecast in Next 48 Hours',
            action_badge='Rain Postponement',
            recommended_runtime_hours=0.0,
            recommended_runtime_formatted='0 hrs 0 mins',
            total_water_litres=0,
            water_litres_per_acre=0,
            optimal_time_window='Not required (Natural rainfall scheduled)',
            irrigation_method=irrigation_method,
            crop_name=crop_name,
            growth_stage=cur_stage,
            kc_factor=kc,
            daily_etc_mm=etc_mm,
            soil_depletion_pct=depletion_pct,
            expected_rain_mm=total_rain,
            reasoning=f'Upcoming precipitation of {total_rain}mm will naturally replenish root-zone soil moisture. Turning off pumps saves ~{int(farm_size_acres * 4.5)} kWh electricity and prevents root waterlogging.',
            power_saving_tip='Ensure farm drainage channels are clear of debris to prevent water stagnation around root collars.'
        )

    # If soil is already wet / waterlogged
    if depletion_pct <= 10:
        return IrrigationPlan(
            action_type='MONITOR',
            action_headline='🟢 MOISTURE ADEQUATE: No Irrigation Needed Today',
            action_badge='Soil Moisture Optimal',
            recommended_runtime_hours=0.0,
            recommended_runtime_formatted='0 hrs 0 mins',
            total_water_litres=0,
            water_litres_per_acre=0,
            optimal_time_window='Check again in 48 hours',
            irrigation_method=irrigation_method,
            crop_name=crop_name,
            growth_stage=cur_stage,
            kc_factor=kc,
            daily_etc_mm=etc_mm,
            soil_depletion_pct=depletion_pct,
            expected_rain_mm=forecast_rain_24h_mm,
            reasoning='Root zone has adequate available water capacity. Additional watering would cause nitrogen leaching and anaerobic root conditions.',
            power_saving_tip='Monitor soil surface tomorrow afternoon before deciding on drip cycle.'
        )

    # 5. Calculate net water depth required (mm)
    # 1 mm water over 1 acre = 4,046.86 Litres
    # Net irrigation depth needed = Daily ETc * (depletion / 40)
    net_irrigation_depth_mm = max(2.0, round(etc_mm * (depletion_pct / 45.0), 2))
    litres_per_acre = int(net_irrigation_depth_mm * 4046.86)
    total_litres = int(litres_per_acre * farm_size_acres)

    # 6. Translate to Method-specific Run Time
    if 'Drip' in irrigation_method:
        # Standard drip system discharge rate ~ 4,000 to 5,000 Litres/acre/hour (using 2.4 LPH drippers spaced 40cm)
        discharge_rate_lph_acre = 4200.0
        runtime_hours = round((litres_per_acre / discharge_rate_lph_acre), 2)
        hrs = int(runtime_hours)
        mins = int((runtime_hours - hrs) * 60)
        formatted_runtime = f'{hrs} hrs {mins} mins'
        time_window = '06:00 AM - 09:30 AM (Low evaporation window)'
    elif 'Sprinkler' in irrigation_method:
        # Standard sprinkler precipitation rate ~ 12 mm/hr
        runtime_hours = round(net_irrigation_depth_mm / 10.0, 2)
        hrs = int(runtime_hours)
        mins = int((runtime_hours - hrs) * 60)
        formatted_runtime = f'{hrs} hrs {mins} mins'
        time_window = '05:30 AM - 08:30 AM (Calm winds)'
    else:
        # Flood / Furrow (5 HP pump ~ 35,000 LPH discharge)
        runtime_hours = round(total_litres / 35000.0, 2)
        hrs = int(runtime_hours)
        mins = int((runtime_hours - hrs) * 60)
        formatted_runtime = f'{hrs} hrs {mins} mins'
        time_window = '06:00 AM - 10:00 AM'

    action_verb = 'IRRIGATE TOMORROW MORNING'
    if depletion_pct >= 65:
        action_verb = 'URGENT: IRRIGATE IMMEDIATELY'

    return IrrigationPlan(
        action_type='IRRIGATE_NOW' if depletion_pct >= 65 else 'IRRIGATE_TOMORROW',
        action_headline=f'💧 {action_verb}: Run {irrigation_method} for {formatted_runtime}',
        action_badge='Recommended Cycle',
        recommended_runtime_hours=runtime_hours,
        recommended_runtime_formatted=formatted_runtime,
        total_water_litres=total_litres,
        water_litres_per_acre=litres_per_acre,
        optimal_time_window=time_window,
        irrigation_method=irrigation_method,
        crop_name=crop_name,
        growth_stage=cur_stage,
        kc_factor=kc,
        daily_etc_mm=etc_mm,
        soil_depletion_pct=depletion_pct,
        expected_rain_mm=forecast_rain_24h_mm,
        reasoning=f'Your {crop_name} is in {cur_stage} with a crop water consumption factor Kc of {kc}. Daily crop evapotranspiration loss is {etc_mm}mm. Soil depletion is at {depletion_pct}%.',
        power_saving_tip=f'Morning irrigation avoids 25% evaporative loss compared to afternoon pumping, saving pump run time.'
    )

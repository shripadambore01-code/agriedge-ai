# AgriEdge AI - Farm Dashboard & Today's Farming Plan Engine
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from backend.farm import FarmProfile, CropStageMetrics, calculate_crop_stage

class FarmingTask(BaseModel):
    id: str
    category: str  # 'Irrigation', 'Fertilizer', 'Pest Scouting', 'Field Activity'
    priority: str  # 'urgent', 'high', 'normal', 'info'
    title: str
    action: str
    why: str
    dosage: Optional[str] = None
    completed: bool = False

class FarmHealthBreakdown(BaseModel):
    soil_score: int
    soil_status: str
    water_score: int
    water_status: str
    pest_risk_score: int
    pest_risk_status: str
    weather_score: int
    weather_status: str

class DashboardSummary(BaseModel):
    overall_health_score: int
    health_status: str
    health_breakdown: FarmHealthBreakdown
    today_tasks: List[FarmingTask]
    crop_metrics: CropStageMetrics

def generate_dashboard_data(profile: FarmProfile) -> DashboardSummary:
    metrics = calculate_crop_stage(
        crop_name=profile.current_crop,
        sowing_date_str=profile.sowing_date,
        variety=profile.variety,
        farm_name=profile.farm_name,
        location=profile.location,
        soil_type=profile.soil_type,
        irrigation_method=profile.irrigation_method,
        farm_size=profile.farm_size
    )

    crop = profile.current_crop
    age = metrics.crop_age_days
    irr = profile.irrigation_method
    soil = profile.soil_type
    size = profile.farm_size

    tasks: List[FarmingTask] = []

    # Dynamic Task Generation based on Crop, Stage, Soil, Irrigation
    if crop == 'Cotton':
        if age <= 20:
            tasks.append(FarmingTask(
                id='task_cot_1',
                category='Field Activity',
                priority='high',
                title='Thinning & Gap Filling',
                action='Remove weak seedlings leaving 1 healthy plant per hill. Fill empty gaps with soaked seeds.',
                why='Ensures optimum plant population of 7,000-10,000 plants per acre.',
                dosage='Maintain 90 cm x 60 cm spacing'
            ))
            tasks.append(FarmingTask(
                id='task_cot_2',
                category='Pest Scouting',
                priority='normal',
                title='Scout for Sucking Pests (Aphids & Thrips)',
                action='Inspect lower surfaces of 20 random leaves across the field.',
                why='Early vegetative stages are prone to jassids and thrips which cause leaf curling.',
                dosage='ETL: 5-10 thrips/leaf'
            ))
        elif age <= 65:
            tasks.append(FarmingTask(
                id='task_cot_3',
                category='Fertilizer',
                priority='urgent',
                title='Top Dressing: Nitrogen & Potassium',
                action=f'Apply Urea and MOP near root zone followed by light {irr.lower()}.',
                why='Squaring and vegetative growth require rapid nitrogen assimilation for node development.',
                dosage=f'Urea @ 25 kg/acre ({size * 25} kg total) + MOP @ 15 kg/acre'
            ))
            tasks.append(FarmingTask(
                id='task_cot_4',
                category='Pest Scouting',
                priority='urgent',
                title='Install Pheromone Traps for Pink Bollworm',
                action='Erect sleeve traps at crop canopy height to monitor adult moth activity.',
                why='Early detection prevents square and flower damage before boll penetration.',
                dosage='5 traps per acre (Install 50 m apart)'
            ))
            tasks.append(FarmingTask(
                id='task_cot_5',
                category='Field Activity',
                priority='normal',
                title='Interculture & De-weeding',
                action='Run shallow blade harrow or manual hand weeding between rows.',
                why='Weed competition at this stage reduces lint yield by up to 30%.',
                dosage='Clear 15 cm strip along drip lateral lines'
            ))
        elif age <= 110:
            tasks.append(FarmingTask(
                id='task_cot_6',
                category='Irrigation',
                priority='urgent',
                title='Critical Flowering & Boll Formation Watering',
                action=f'Maintain steady moisture using {irr.lower()}. Avoid water stress or over-flooding.',
                why='Moisture stress during flowering causes massive flower and young boll shedding.',
                dosage='Run drip for 2.5 - 3 hours every alternate day'
            ))
            tasks.append(FarmingTask(
                id='task_cot_7',
                category='Fertilizer',
                priority='high',
                title='Foliar 13:0:45 (Potassium Nitrate) Spray',
                action='Foliar spray of Potassium Nitrate + 0.1% Boron during morning hours.',
                why='Enhances boll size, prevents parawilt, and increases fiber tensile strength.',
                dosage='10 g/liter of water (1.5 kg per acre)'
            ))
        else:
            tasks.append(FarmingTask(
                id='task_cot_8',
                category='Field Activity',
                priority='high',
                title='First Picking of Open Bolls',
                action='Pick fully opened dry bolls into clean cotton bags. Avoid morning dew wet picking.',
                why='Prevents yellow staining of lint and trash contamination.',
                dosage='Sort clean bolls from stained bolls immediately'
            ))
    elif crop == 'Wheat':
        if age <= 25:
            tasks.append(FarmingTask(
                id='task_wht_1',
                category='Irrigation',
                priority='urgent',
                title='First CRI Stage Irrigation',
                action=f'Provide first and most critical irrigation at Crown Root Initiation (Day 20-22).',
                why='Roots establish now; missing this irrigation cuts yield by 25-30%.',
                dosage='Light uniform irrigation of 5-6 cm depth'
            ))
            tasks.append(FarmingTask(
                id='task_wht_2',
                category='Fertilizer',
                priority='high',
                title='First Urea Top Dressing',
                action='Broadcast Urea just after first irrigation when soil is in workable moisture.',
                why='Boosts tiller initiation and leaf chlorophyll.',
                dosage=f'Urea @ 30 kg/acre ({size * 30} kg total)'
            ))
        elif age <= 70:
            tasks.append(FarmingTask(
                id='task_wht_3',
                category='Pest Scouting',
                priority='urgent',
                title='Inspect for Yellow Rust Pustules',
                action='Inspect upper leaves for yellowish-orange powdery linear stripes.',
                why='Cool moist morning weather favors rapid fungal spore germination.',
                dosage='If observed: Spray Propiconazole 25% EC @ 1 ml/L'
            ))
        else:
            tasks.append(FarmingTask(
                id='task_wht_4',
                category='Irrigation',
                priority='high',
                title='Milk & Dough Stage Irrigation',
                action='Provide light irrigation during calm wind hours to prevent lodging.',
                why='Grain filling determines 1000-grain weight and test weight.',
                dosage='Avoid irrigation during high wind forecast'
            ))
    elif crop == 'Tomato':
        tasks.append(FarmingTask(
            id='task_tom_1',
            category='Pest Scouting',
            priority='urgent',
            title='Check for Early Blight & Whitefly',
            action='Scout lower leaves for target-board brown concentric rings and whitefly underside leaves.',
            why='High humidity triggers fungal blights and viral leaf curl transmission.',
            dosage='Mancozeb 75% WP @ 2.5 g/liter or Neem Oil 10,000 ppm @ 2 ml/L'
        ))
        tasks.append(FarmingTask(
            id='task_tom_2',
            category='Fertilizer',
            priority='high',
            title='Calcium Nitrate & Boron Fertigation',
            action=f'Inject water soluble Calcium Nitrate through {irr.lower()}.',
            why='Prevents Blossom End Rot (black base on fruit) and enhances skin shine.',
            dosage=f'Calcium Nitrate @ 3 kg/acre ({size * 3} kg total)'
        ))
        tasks.append(FarmingTask(
            id='task_tom_3',
            category='Field Activity',
            priority='normal',
            title='Staking & Trellising Support',
            action='Tie growing tomato vines to bamboo stakes or trellising twine.',
            why='Keeps fruit off soil, improves aeration, and avoids soil-borne rotting.',
            dosage='Tie loosely with jute twine'
        ))
    else:
        tasks.append(FarmingTask(
            id='task_gen_1',
            category='Field Activity',
            priority='high',
            title=f'{crop} Growth Monitoring & Weed Management',
            action=f'Inspect field for crop vigor, tiller/branch density and remove competing weed flora.',
            why=f'Crop is at day {age} ({metrics.current_stage_name}); weed suppression maximizes fertilizer uptake.',
            dosage='Hand weeding or shallow hoeing'
        ))
        tasks.append(FarmingTask(
            id='task_gen_2',
            category='Irrigation',
            priority='normal',
            title=f'Check Soil Moisture for {irr}',
            action=f'Test soil moisture at 10-15 cm root depth before running {irr.lower()}.',
            why='Prevents over-saturation and root asphyxiation in ' + soil + '.',
            dosage='Maintain 65-70% field capacity'
        ))
        tasks.append(FarmingTask(
            id='task_gen_3',
            category='Fertilizer',
            priority='normal',
            title='Balanced Macronutrient Top-Dressing',
            action='Apply nitrogen top dressing based on soil test recommendations.',
            why='Supports ongoing vegetative and canopy expansion.',
            dosage='Urea @ 20 kg/acre with irrigation'
        ))

    # Health score calculations
    soil_score = 88 if 'Black' in soil or 'Alluvial' in soil else 82
    water_score = 92 if 'Drip' in irr else (84 if 'Sprinkler' in irr else 78)
    pest_risk_score = 82 if age < 70 else 76
    weather_score = 88

    overall_score = round((soil_score * 0.25) + (water_score * 0.3) + (pest_risk_score * 0.25) + (weather_score * 0.2))

    if overall_score >= 85:
        health_status = 'Optimal Condition'
    elif overall_score >= 70:
        health_status = 'Good Condition'
    else:
        health_status = 'Attention Needed'

    breakdown = FarmHealthBreakdown(
        soil_score=soil_score,
        soil_status='Rich Organic Matter' if soil_score >= 85 else 'Good Structure',
        water_score=water_score,
        water_status='High Efficiency' if 'Drip' in irr else 'Adequate Moisture',
        pest_risk_score=pest_risk_score,
        pest_risk_status='Low to Moderate Risk',
        weather_score=weather_score,
        weather_status='Favorable Season'
    )

    return DashboardSummary(
        overall_health_score=overall_score,
        health_status=health_status,
        health_breakdown=breakdown,
        today_tasks=tasks,
        crop_metrics=metrics
    )

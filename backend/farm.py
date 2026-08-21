# Farm Profile & Crop Stage Engine
from datetime import datetime, date
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

CROP_LIFECYCLES = {
    "Cotton": {
        "duration_days": 160,
        "stages": [
            {"name": "Germination & Emergence", "start": 0, "end": 12, "desc": "Seed sprouting, cotyledon emergence, root establishment."},
            {"name": "Early Vegetative", "start": 13, "end": 35, "desc": "Main stem growth, first true leaves, node development."},
            {"name": "Squaring & Branching", "start": 36, "end": 65, "desc": "Appearance of floral buds (squares), rapid canopy growth."},
            {"name": "Flowering & Boll Setting", "start": 66, "end": 105, "desc": "Peak flowering, pollination, young boll formation. Critical water need."},
            {"name": "Boll Maturation & Opening", "start": 106, "end": 140, "desc": "Boll filling, fiber elongation, early boll bursting."},
            {"name": "Harvest Readiness", "start": 141, "end": 180, "desc": "Fluffy open bolls ready for picking. Dry weather required."}
        ]
    },
    "Wheat": {
        "duration_days": 125,
        "stages": [
            {"name": "Crown Root Initiation (CRI)", "start": 0, "end": 22, "desc": "Critical first irrigation stage, crown root establishment."},
            {"name": "Tillering Stage", "start": 23, "end": 45, "desc": "Secondary shoot production, high nutrient uptake."},
            {"name": "Jointing & Stem Elongation", "start": 46, "end": 70, "desc": "Nodes pushing upward, rapid leaf and canopy expansion."},
            {"name": "Booting & Heading", "start": 71, "end": 90, "desc": "Emergence of wheat ears/spikes, flowering."},
            {"name": "Grain Milking & Dough Stage", "start": 91, "end": 110, "desc": "Kernel filling from milky to dough consistency."},
            {"name": "Maturity & Harvest", "start": 111, "end": 135, "desc": "Golden yellow straw, grain moisture under 12%, ready for combining."}
        ]
    },
    "Rice / Paddy": {
        "duration_days": 130,
        "stages": [
            {"name": "Nursery & Transplanting", "start": 0, "end": 25, "desc": "Seedling growth in nursery followed by field transplanting."},
            {"name": "Tillering & Rooting", "start": 26, "end": 50, "desc": "Active vegetative growth, panicle initiation."},
            {"name": "Stem Elongation & Panicle Development", "start": 51, "end": 75, "desc": "Booting stage, flag leaf expansion."},
            {"name": "Heading & Flowering", "start": 76, "end": 95, "desc": "Panicle exertion, anthesis, pollination."},
            {"name": "Milk & Dough Grain Filling", "start": 96, "end": 115, "desc": "Starch accumulation in grains."},
            {"name": "Ripening & Harvesting", "start": 116, "end": 140, "desc": "85% grains golden yellow, drain standing water for harvest."}
        ]
    },
    "Tomato": {
        "duration_days": 110,
        "stages": [
            {"name": "Nursery & Establishment", "start": 0, "end": 20, "desc": "Transplant shock recovery, vegetative root growth."},
            {"name": "Active Vegetative & Branching", "start": 21, "end": 40, "desc": "Foliage expansion, side shoots development."},
            {"name": "First Flowering & Fruit Set", "start": 41, "end": 60, "desc": "Yellow blossom clusters, pea-sized fruit setting."},
            {"name": "Fruit Development & Sizing", "start": 61, "end": 85, "desc": "Rapid fruit expansion, high potassium demand."},
            {"name": "Color Break & Harvesting", "start": 86, "end": 120, "desc": "Breaker to red ripe stage, continuous picking."}
        ]
    },
    "Sugarcane": {
        "duration_days": 360,
        "stages": [
            {"name": "Germination Phase", "start": 0, "end": 45, "desc": "Sprouting of setts, root emergence."},
            {"name": "Tillering Phase", "start": 46, "end": 120, "desc": "Profuse tillering, canopy closure."},
            {"name": "Grand Growth Phase", "start": 121, "end": 270, "desc": "Rapid cane elongation, internode formation, maximum water need."},
            {"name": "Ripening & Maturation", "start": 271, "end": 365, "desc": "Sucrose synthesis and storage in stalks, dry period favored."}
        ]
    },
    "Soybean": {
        "duration_days": 95,
        "stages": [
            {"name": "Emergence & Cotyledon", "start": 0, "end": 12, "desc": "Seed germination, unifoliolate leaf appearance."},
            {"name": "Vegetative & Nodulation", "start": 13, "end": 35, "desc": "Trifoliate leaves, Rhizobium nitrogen fixation."},
            {"name": "Flowering (R1-R2)", "start": 36, "end": 55, "desc": "Purple or white blooms on nodes, critical moisture period."},
            {"name": "Pod Formation & Seed Filling", "start": 56, "end": 80, "desc": "Pod elongation and bean expansion."},
            {"name": "Full Maturity & Defoliation", "start": 81, "end": 105, "desc": "Leaves turn yellow and drop, pods turn brown, ready to thresh."}
        ]
    },
    "Maize": {
        "duration_days": 105,
        "stages": [
            {"name": "Seedling & Emergence", "start": 0, "end": 18, "desc": "Coleoptile emergence, V2-V4 leaf collar stages."},
            {"name": "Knee-High Vegetative (V6-V10)", "start": 19, "end": 42, "desc": "Rapid vertical growth, ear shoot initiation."},
            {"name": "Tasseling & Silking", "start": 43, "end": 65, "desc": "Tassel pollen shed, silk emergence, pollination."},
            {"name": "Blister & Milk Kernel Filling", "start": 66, "end": 85, "desc": "Kernels fill with starch fluid."},
            {"name": "Black Layer & Harvest", "start": 86, "end": 115, "desc": "Physiological maturity, kernel moisture drops, harvest ready."}
        ]
    },
    "Onion": {
        "duration_days": 120,
        "stages": [
            {"name": "Transplanting & Rooting", "start": 0, "end": 20, "desc": "Seedling establishment, rooting."},
            {"name": "Foliage Development", "start": 21, "end": 50, "desc": "Leaf blade expansion (8-10 leaves target)."},
            {"name": "Bulb Initiation", "start": 51, "end": 80, "desc": "Photoperiod trigger, neck thickening, bulb base swelling."},
            {"name": "Bulb Enlargement", "start": 81, "end": 105, "desc": "Rapid bulb growth, stop nitrogen top dressing."},
            {"name": "Neck Fall & Curing", "start": 106, "end": 130, "desc": "50% top fall, field drying, skin hardening for storage."}
        ]
    },
    "General / Other Crop": {
        "duration_days": 120,
        "stages": [
            {"name": "Germination & Seedling", "start": 0, "end": 20, "desc": "Sprouting and initial vegetative establishment."},
            {"name": "Vegetative Growth", "start": 21, "end": 50, "desc": "Foliage and canopy development."},
            {"name": "Flowering & Reproductive", "start": 51, "end": 80, "desc": "Bloom appearance, pollination, fruit/seed setting."},
            {"name": "Maturation & Ripening", "start": 81, "end": 110, "desc": "Yield filling, color change, ripening."},
            {"name": "Harvest Readiness", "start": 111, "end": 130, "desc": "Crop ready for harvesting."}
        ]
    }
}

class FarmProfile(BaseModel):
    farm_name: str = Field(default="Green Acres Farm", description="Name of the farm or field")
    farmer_name: str = Field(default="Farmer", description="Name of the farmer")
    location: str = Field(default="Nashik, Maharashtra", description="District, State, Country")
    farm_size: float = Field(default=3.0, description="Farm size in acres")
    soil_type: str = Field(default="Black Soil / Regur", description="Soil classification")
    irrigation_method: str = Field(default="Drip Irrigation", description="Irrigation system")
    current_crop: str = Field(default="Cotton", description="Main crop being cultivated")
    variety: str = Field(default="BT Cotton Hybrid", description="Crop variety or seed brand")
    sowing_date: str = Field(default_factory=lambda: date.today().strftime("%Y-%m-%d"), description="Date of sowing (YYYY-MM-DD)")
    expected_harvest_date: Optional[str] = Field(default=None, description="Estimated harvest date (YYYY-MM-DD)")

class CropStageMetrics(BaseModel):
    crop_name: str
    variety: str
    sowing_date: str
    crop_age_days: int
    total_duration_days: int
    progress_percentage: float
    current_stage_name: str
    current_stage_description: str
    days_to_harvest: int
    stage_index: int
    total_stages: int
    all_stages: List[Dict[str, Any]]
    personalized_summary: str

def calculate_crop_stage(crop_name: str, sowing_date_str: str, variety: str = '', farm_name: str = '', location: str = '', soil_type: str = '', irrigation_method: str = '', farm_size: float = 1.0) -> CropStageMetrics:
    try:
        sowing_dt = datetime.strptime(sowing_date_str, '%Y-%m-%d').date()
    except Exception:
        sowing_dt = date.today()

    today = date.today()
    crop_age = max(0, (today - sowing_dt).days)

    crop_info = CROP_LIFECYCLES.get(crop_name, CROP_LIFECYCLES['General / Other Crop'])
    total_duration = crop_info['duration_days']
    stages = crop_info['stages']

    current_stage = stages[-1]
    stage_idx = len(stages) - 1

    for idx, stg in enumerate(stages):
        if stg['start'] <= crop_age <= stg['end']:
            current_stage = stg
            stage_idx = idx
            break
        elif crop_age < stg['start']:
            current_stage = stages[max(0, idx - 1)]
            stage_idx = max(0, idx - 1)
            break

    progress_pct = min(100.0, round((crop_age / total_duration) * 100.0, 1))
    days_remaining = max(0, total_duration - crop_age)

    summary = (
        f"Farm: '{farm_name or 'My Farm'}' in {location or 'India'}. "
        f"Farm Size: {farm_size} acres, Soil: {soil_type or 'General'}, Irrigation: {irrigation_method or 'Standard'}. "
        f"Crop: {crop_name} (Variety: {variety or 'Standard'}), Sown on {sowing_date_str} (Day {crop_age} of ~{total_duration} days, {progress_pct}% completed). "
        f"Current Growth Stage: '{current_stage['name']}' ({current_stage['desc']}). "
        f"Estimated {days_remaining} days remaining until harvest."
    )

    return CropStageMetrics(
        crop_name=crop_name,
        variety=variety or "Standard",
        sowing_date=sowing_date_str,
        crop_age_days=crop_age,
        total_duration_days=total_duration,
        progress_percentage=progress_pct,
        current_stage_name=current_stage["name"],
        current_stage_description=current_stage["desc"],
        days_to_harvest=days_remaining,
        stage_index=stage_idx,
        total_stages=len(stages),
        all_stages=stages,
        personalized_summary=summary
    )

# AgriEdge AI - Detailed Crop Lifecycle Journey & Agronomic Guide Engine
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime, date
from backend.farm import calculate_crop_stage, CROP_LIFECYCLES

class StageAgronomicDetails(BaseModel):
    stage_id: str
    stage_number: int
    name: str
    day_start: int
    day_end: int
    is_current: bool
    is_past: bool
    is_future: bool
    days_remaining_in_stage: int
    status_label: str
    scientific_summary: str
    key_dos: List[str]
    key_donts: List[str]
    pest_threats: List[str]
    nutrient_focus: str
    irrigation_need: str

class CropJourneyTimeline(BaseModel):
    crop_name: str
    variety: str
    sowing_date: str
    crop_age_days: int
    total_duration_days: int
    progress_percentage: float
    current_stage_name: str
    days_to_harvest: int
    days_to_next_stage: int
    stages: List[StageAgronomicDetails]

STAGE_AGRONOMIC_KNOWLEDGE: Dict[str, Dict[str, Dict[str, Any]]] = {
    'Cotton': {
        'Germination & Emergence': {
            'summary': 'Radicle emergence and cotyledon opening. Taproot establishes anchorage and seeks subsoil moisture.',
            'dos': ['Maintain moist seedbed without water stagnation', 'Treat seeds with Imidacloprid 600 FS @ 5ml/kg', 'Inspect for cutworms and seedling wilt'],
            'donts': ['Do not allow crust formation over seedlings', 'Avoid heavy flood irrigation', 'Do not apply high doses of chemical nitrogen near tender roots'],
            'threats': ['Cutworms', 'Seedling Blight / Rhizoctonia', 'Termites'],
            'nutrient': 'Basal SSP (Phosphorus) + FYM Organic Manure',
            'irrigation': 'Light uniform watering (Field capacity 60%)'
        },
        'Early Vegetative': {
            'summary': 'Main stem node elongation, first 5-8 true leaves unfold, and lateral root branching expands rapidly.',
            'dos': ['Thin out weak plants to 1 healthy seedling per hill at Day 15-20', 'Hoe shallowly to aerate root zone and kill young weeds', 'Foliar spray 19:19:19 @ 5g/L for vegetative boost'],
            'donts': ['Do not delay weeding past 25 days (critical weed competition period)', 'Avoid herbicide drift from adjacent plots', 'Do not allow water to stand at root collar'],
            'threats': ['Jassids (Leafhoppers)', 'Aphids', 'Thrips', 'Fusarium Wilt'],
            'nutrient': 'Urea @ 20 kg/acre + Micronutrient Zinc Sulphate',
            'irrigation': 'Irrigate every 7-10 days depending on soil texture'
        },
        'Squaring & Branching': {
            'summary': 'Sympodial (fruiting) branches develop. Floral buds (squares) appear on nodes. Critical stage for fruit initiation.',
            'dos': ['Install 5 Pheromone Traps per acre for Pink Bollworm monitoring', 'Apply second split of Nitrogen + Potash', 'Spray Boron 0.1% to prevent square drop'],
            'donts': ['Avoid excessive synthetic pyrethroids (sparks secondary whitefly surge)', 'Do not let soil dry out into cracking moisture stress', 'Avoid excess vegetative nitrogen that causes lanky growth'],
            'threats': ['Pink Bollworm (Early Moth Influx)', 'Spotted Bollworm', 'Mirid Bugs', 'Alternaria Leaf Spot'],
            'nutrient': 'Urea @ 25 kg/acre + MOP (Potash) @ 15 kg/acre',
            'irrigation': 'Maintain regular 4-5 day drip cycle'
        },
        'Flowering & Boll Setting': {
            'summary': 'Cream-colored flowers bloom and turn pink/red after pollination. Young bolls form and accumulate fiber mass.',
            'dos': ['Maintain steady moisture — peak water consumption stage of crop lifecycle', 'Foliar spray 13:0:45 (Potassium Nitrate) @ 10g/L', 'Scout 20 green bolls per acre for internal pink bollworm larvae'],
            'donts': ['NEVER let crop suffer moisture stress (leads to 40%+ boll shedding)', 'Do not spray chemicals during peak morning bee foraging (7-10 AM)', 'Do not over-irrigate causing root asphyxiation'],
            'threats': ['Pink Bollworm', 'American Bollworm (Helicoverpa)', 'Grey Mildew', 'Bacterial Blight'],
            'nutrient': 'Foliar 13:0:45 + 0.1% Boron + Magnesium Sulphate',
            'irrigation': 'Critical peak irrigation (Drip 2.5 - 3 hours alternate day)'
        },
        'Boll Maturation & Opening': {
            'summary': 'Bolls reach maximum size, carpels dry, and bolls begin cracking open to expose white fluffy cotton lint.',
            'dos': ['Cease soil nitrogen applications to promote natural dry-down and boll cracking', 'Ensure field is free of spiny weeds before picking', 'Provide light terminal irrigation to finish upper bolls'],
            'donts': ['Do not apply late nitrogen which causes vegetative regrowth', 'Do not flood fields during boll opening (causes lint rotting and staining)', 'Avoid harvesting dew-wet bolls'],
            'threats': ['Late Pink Bollworm', 'Cotton Stainer Bug', 'Boll Rot / Aspergillus'],
            'nutrient': 'Zero soil nitrogen; optional foliar Potassium if top bolls need finishing',
            'irrigation': 'Taper off irrigation gradually'
        },
        'Harvest Readiness': {
            'summary': '80-90% bolls naturally open. Dry crisp bracts ready for clean manual picking.',
            'dos': ['Pick fully opened bolls into clean 100% cotton cloths/bags', 'Dry picked seed cotton in shade on clean tarpaulins', 'Store in dry moisture-proof room with <8% moisture content'],
            'donts': ['Do not use polypropylene / plastic bags (causes contamination penalty at ginning mills)', 'Do not mix stained/damaged cotton with prime grade pickings', 'Do not leave stalks standing for ratoon crop (harbors overwintering pink bollworm)'],
            'threats': ['Post-harvest trash contamination', 'Moisture staining'],
            'nutrient': 'None',
            'irrigation': 'Completely stopped'
        }
    }
}

def get_crop_journey_timeline(crop_name: str, sowing_date_str: str, variety: str = '', farm_size: float = 1.0) -> CropJourneyTimeline:
    metrics = calculate_crop_stage(crop_name=crop_name, sowing_date_str=sowing_date_str, variety=variety, farm_size=farm_size)
    age = metrics.crop_age_days

    crop_cfg = CROP_LIFECYCLES.get(crop_name, CROP_LIFECYCLES.get('Cotton'))
    raw_stages = crop_cfg['stages']
    total_duration = crop_cfg['duration_days']
    agronomic_dict = STAGE_AGRONOMIC_KNOWLEDGE.get(crop_name, STAGE_AGRONOMIC_KNOWLEDGE.get('Cotton'))

    stage_details_list: List[StageAgronomicDetails] = []
    days_to_next = 0

    for i, s in enumerate(raw_stages):
        is_cur = (age >= s['start'] and age <= s['end']) or (i == len(raw_stages)-1 and age > s['end'])
        is_past = age > s['end'] and not is_cur
        is_future = age < s['start']

        if is_cur:
            days_to_next = max(0, s['end'] - age)

        k_info = agronomic_dict.get(s['name'], {
            'summary': f"{s['name']} stage of {crop_name}. Critical for physiological growth.",
            'dos': ['Maintain regular irrigation and weed control', 'Inspect field for nutrient deficiencies', 'Monitor for pest infestations'],
            'donts': ['Avoid moisture stress', 'Do not apply unrecommended chemicals', 'Avoid delayed interventions'],
            'threats': ['Common chewing pests', 'Fungal pathogens'],
            'nutrient': 'Balanced NPK according to stage',
            'irrigation': 'Normal scheduled irrigation'
        })

        rem_in_stage = max(0, s['end'] - age) if is_cur else 0
        status_lbl = 'Active Stage' if is_cur else ('Completed' if is_past else 'Upcoming')

        stage_details_list.append(StageAgronomicDetails(
            stage_id=f'stage_{i+1}',
            stage_number=i+1,
            name=s['name'],
            day_start=s['start'],
            day_end=s['end'],
            is_current=is_cur,
            is_past=is_past,
            is_future=is_future,
            days_remaining_in_stage=rem_in_stage,
            status_label=status_lbl,
            scientific_summary=k_info['summary'],
            key_dos=k_info['dos'],
            key_donts=k_info['donts'],
            pest_threats=k_info['threats'],
            nutrient_focus=k_info['nutrient'],
            irrigation_need=k_info['irrigation']
        ))

    return CropJourneyTimeline(
        crop_name=crop_name,
        variety=variety or 'Standard Hybrid',
        sowing_date=sowing_date_str,
        crop_age_days=age,
        total_duration_days=total_duration,
        progress_percentage=metrics.progress_percentage,
        current_stage_name=metrics.current_stage_name,
        days_to_harvest=metrics.days_to_harvest,
        days_to_next_stage=days_to_next,
        stages=stage_details_list
    )

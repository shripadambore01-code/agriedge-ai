# AgriEdge AI - Government Scheme Matching & Subsidy Application Assistant
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class SchemeCard(BaseModel):
    id: str
    name: str
    ministry_or_dept: str
    scheme_type: str  # 'Direct Cash Transfer', 'Capital Subsidy', 'Risk Insurance', 'Input Support'
    benefit_summary: str
    eligibility_status: str  # 'Eligible 🟢', 'Highly Recommended 🟢', 'Conditionally Eligible 🟡'
    eligibility_reason: str
    estimated_benefit_inr: float
    required_documents: List[str]
    how_to_apply: List[str]
    official_portal_url: str

class SchemeMatchResponse(BaseModel):
    farmer_name: str
    location: str
    farm_size_acres: float
    farmer_category: str  # 'Marginal Farmer (<2.5 Acres)', 'Small Farmer (2.5-5 Acres)', 'Medium Farmer (5-10 Acres)'
    crop_name: str
    total_potential_benefit_inr: float
    matched_count: int
    matched_schemes: List[SchemeCard]

ALL_GOVT_SCHEMES: List[Dict[str, Any]] = [
    {
        'id': 'pm_kisan',
        'name': 'PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)',
        'ministry': 'Ministry of Agriculture & Farmers Welfare',
        'type': 'Direct Cash Transfer',
        'base_benefit': 6000.0,
        'portal': 'https://pmkisan.gov.in/',
        'documents': [
            'Aadhaar Card linked to Mobile Number',
            'Land Record (7/12 Extract, Khatoni, or RoR)',
            'Active Bank Account Passbook (Aadhaar Seeded / NPCI Direct)',
            'Self-Declaration Form'
        ],
        'steps': [
            'Visit pmkisan.gov.in and click on "New Farmer Registration"',
            'Enter Aadhaar number and select your State and District',
            'Verify Aadhaar via OTP sent to your linked mobile number',
            'Enter land survey numbers and bank IFSC details, then submit for State nodal verification'
        ]
    },
    {
        'id': 'pmfby',
        'name': 'PMFBY (Pradhan Mantri Fasal Bima Yojana)',
        'ministry': 'Ministry of Agriculture & Farmers Welfare',
        'type': 'Crop Risk Insurance',
        'base_benefit': 45000.0,
        'portal': 'https://pmfby.gov.in/',
        'documents': [
            'Land Record (RoR / 7/12 Extract / Khasra)',
            'Sowing Certificate / Patwari Crop Sown Certificate',
            'Bank Account Passbook Copy',
            'Aadhaar Card & Identity Proof'
        ],
        'steps': [
            'Visit pmfby.gov.in or approach your local Common Service Center (CSC) or Bank branch',
            'Select Kharif / Rabi season, crop name, and district notification unit',
            'Pay nominal subsidized farmer premium (1.5% for Rabi, 2.0% for Kharif, 5% for Horticulture)',
            'Collect insurance policy receipt before the seasonal cut-off deadline'
        ]
    },
    {
        'id': 'pmksy_micro_irrigation',
        'name': 'PMKSY - Per Drop More Crop (Micro-Irrigation Subsidy)',
        'ministry': 'Department of Agriculture & Farmers Welfare',
        'type': 'Equipment Subsidy',
        'base_benefit': 55000.0,
        'portal': 'https://pmksy.gov.in/',
        'documents': [
            'Land Ownership Title (7/12 / 8A / Jamabandi)',
            'Soil & Water Source Certificate (Well/Borewell availability)',
            'Aadhaar Card & Passport Size Photo',
            'Quotation from Authorized Drip/Sprinkler Manufacturer'
        ],
        'steps': [
            'Register on your state agriculture/horticulture DBT portal (e.g. Mahadbt, e-Kisan, HORTNET)',
            'Upload land record and water availability proof',
            'Select approved micro-irrigation vendor for GPS field survey and CAD design quotation',
            'Receive 45% to 55% direct subsidy on total system cost post physical field verification'
        ]
    },
    {
        'id': 'pm_kusum',
        'name': 'PM-KUSUM (Solar Agriculture Water Pump Subsidy)',
        'ministry': 'Ministry of New and Renewable Energy',
        'type': 'Capital Subsidy',
        'base_benefit': 120000.0,
        'portal': 'https://pmkusum.mnre.gov.in/',
        'documents': [
            'Land Holding Document (Khasra/Khatauni/7-12)',
            'Aadhaar Card & Bank Account Details',
            'Certificate of No Electric Agricultural Connection on Survey No.',
            'Underground Water Table NOC / Feasibility Report'
        ],
        'steps': [
            'Apply on State Renewable Energy Portal (e.g. MEDA, UPNEDA, HAREDA)',
            'Pay 10% farmer share; Central Govt provides 30% and State Govt provides 30% subsidy',
            'Avail remaining 30% via low-interest bank loan',
            'Authorized vendor installs 3HP to 7.5HP Solar DC/AC Pump with 5-year warranty'
        ]
    },
    {
        'id': 'smam_mechanization',
        'name': 'SMAM (Sub-Mission on Agricultural Mechanization)',
        'ministry': 'Ministry of Agriculture & Farmers Welfare',
        'type': 'Farm Machinery Subsidy',
        'base_benefit': 40000.0,
        'portal': 'https://agrimachinery.nic.in/',
        'documents': [
            'Aadhaar Card',
            'Land Record (RoR)',
            'Bank Passbook Copy',
            'Caste Certificate (for SC/ST/Small/Marginal women farmers priority)'
        ],
        'steps': [
            'Register on agrimachinery.nic.in DBT portal',
            'Choose farm machinery (Rotavator, Seed Drill, Power Weeder, Sprayer)',
            'Receive subsidy sanction order and purchase machinery from registered dealer',
            'Subsidy amount (40% to 50%) is credited directly into farmer bank account'
        ]
    },
    {
        'id': 'soil_health_card',
        'name': 'National Soil Health Card Scheme',
        'ministry': 'Department of Agriculture & Farmers Welfare',
        'type': 'Free Laboratory Testing',
        'base_benefit': 1500.0,
        'portal': 'https://soilhealth.dac.gov.in/',
        'documents': [
            'Farmer Aadhaar Number',
            'Survey / Khasra Number of Farm'
        ],
        'steps': [
            'Agriculture officer / Krishi Mitra collects GPS-tagged soil sample from your farm',
            'Sample is analyzed for 12 parameters (pH, EC, OC, N, P, K, S, Zn, Fe, Cu, Mn, B) in testing lab',
            'Receive official physical Soil Health Card with crop-wise fertilizer dosage recommendations free of cost'
        ]
    }
]

def match_government_schemes(
    farmer_name: str = "Farmer",
    location: str = "Maharashtra, India",
    farm_size_acres: float = 3.0,
    crop_name: str = "Cotton",
    irrigation_method: str = "Drip Irrigation"
) -> SchemeMatchResponse:
    """Matches agricultural schemes and calculates potential financial benefits."""
    
    # 1. Categorize Farmer
    if farm_size_acres <= 2.5:
        category = "Marginal Farmer (< 1 Hectare / 2.5 Acres)"
    elif farm_size_acres <= 5.0:
        category = "Small Farmer (1-2 Hectares / 2.5-5.0 Acres)"
    elif farm_size_acres <= 10.0:
        category = "Semi-Medium Farmer (2-4 Hectares / 5-10 Acres)"
    else:
        category = "Large Farmer (> 4 Hectares / >10 Acres)"

    matched: List[SchemeCard] = []
    total_benefit = 0.0

    for s in ALL_GOVT_SCHEMES:
        s_id = s['id']
        benefit_val = s['base_benefit']
        status = "Eligible 🟢"
        reason = "Meets landholding and agricultural eligibility criteria."

        if s_id == 'pm_kisan':
            benefit_summary = "₹6,000 / year paid directly in 3 equal installments of ₹2,000 into bank account via DBT."
            reason = f"All landholding farmer families qualifying under operational guidelines are eligible."
        elif s_id == 'pmfby':
            benefit_val = round(farm_size_acres * 25000.0, 0)
            benefit_summary = f"Comprehensive insurance coverage up to ₹{benefit_val:,.0f} against drought, flood, pests, and unseasonal rainfall."
            status = "Highly Recommended 🟢"
            reason = f"Notified for {crop_name} in your district with nominal 1.5% - 2% premium."
        elif s_id == 'pmksy_micro_irrigation':
            benefit_val = round(farm_size_acres * 22000.0, 0)
            benefit_summary = f"Up to 55% capital subsidy (approx. ₹{benefit_val:,.0f}) for installing or expanding Drip / Sprinkler system."
            status = "Eligible 🟢" if ("Drip" in irrigation_method or "Sprinkler" in irrigation_method) else "Conditionally Eligible 🟡"
            reason = f"Small/Marginal farmers receive 55% subsidy, others receive 45% under Per Drop More Crop."
        elif s_id == 'pm_kusum':
            benefit_val = 145000.0
            benefit_summary = "60% combined Central + State subsidy for standalone 3HP to 7.5HP off-grid Solar Agriculture Water Pump."
            status = "Eligible 🟢"
            reason = "Farmers with agriculture land and well/borewell water source qualify for Component B."
        elif s_id == 'smam_mechanization':
            benefit_val = 45000.0
            benefit_summary = "40% to 50% subsidy on purchase of Rotavators, Multi-Crop Seed Drills, Boom Sprayers, and Power Weeders."
            status = "Eligible 🟢"
            reason = f"Special 50% subsidy allocation for {category}."
        elif s_id == 'soil_health_card':
            benefit_val = 1500.0
            benefit_summary = "100% Free laboratory testing of farm soil across 12 macro and micro nutrients with customized crop cards."
            status = "Eligible 🟢"
            reason = "Free service provided by Ministry of Agriculture every 2 years."
        else:
            benefit_summary = "Government agricultural assistance."

        total_benefit += benefit_val

        matched.append(SchemeCard(
            id=s_id,
            name=s['name'],
            ministry_or_dept=s['ministry'],
            scheme_type=s['type'],
            benefit_summary=benefit_summary,
            eligibility_status=status,
            eligibility_reason=reason,
            estimated_benefit_inr=benefit_val,
            required_documents=s['documents'],
            how_to_apply=s['steps'],
            official_portal_url=s['portal']
        ))

    return SchemeMatchResponse(
        farmer_name=farmer_name,
        location=location,
        farm_size_acres=farm_size_acres,
        farmer_category=category,
        crop_name=crop_name,
        total_potential_benefit_inr=total_benefit,
        matched_count=len(matched),
        matched_schemes=matched
    )

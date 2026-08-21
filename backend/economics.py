# AgriEdge AI - Farm Economics, Cost of Cultivation & Mandi Profit Calculator Engine
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class CostItem(BaseModel):
    category: str
    amount_inr: float
    per_acre_inr: float
    description: str

class EconomicsReport(BaseModel):
    crop_name: str
    variety: str
    farm_size_acres: float
    expected_yield_per_acre_qtl: float
    total_expected_yield_qtl: float
    current_mandi_price_per_qtl: float
    msp_benchmark_price_per_qtl: float
    price_trend: str  # 'Rising 📈', 'Stable ⚖️', 'Falling 📉'
    gross_revenue_inr: float
    total_cost_inr: float
    net_profit_inr: float
    roi_percentage: float
    production_cost_per_qtl: float
    breakeven_price_per_qtl: float
    costs_breakdown: List[CostItem]
    market_selling_advisory: str

# Standard Baseline Costs of Cultivation per Acre (INR)
CROP_COST_BENCHMARKS: Dict[str, Dict[str, float]] = {
    'Cotton': {
        'seeds': 2400.0,
        'fertilizers': 4800.0,
        'pesticides': 3500.0,
        'labor': 9500.0,
        'irrigation_power': 2000.0,
        'machinery_rental': 3000.0
    },
    'Wheat': {
        'seeds': 1800.0,
        'fertilizers': 3600.0,
        'pesticides': 1500.0,
        'labor': 4500.0,
        'irrigation_power': 2200.0,
        'machinery_rental': 3500.0
    },
    'Rice / Paddy': {
        'seeds': 1500.0,
        'fertilizers': 3800.0,
        'pesticides': 2200.0,
        'labor': 8500.0,
        'irrigation_power': 3000.0,
        'machinery_rental': 3500.0
    },
    'Tomato': {
        'seeds': 4500.0,
        'fertilizers': 7500.0,
        'pesticides': 6000.0,
        'labor': 14000.0,
        'irrigation_power': 3500.0,
        'machinery_rental': 3000.0
    },
    'Sugarcane': {
        'seeds': 8000.0,
        'fertilizers': 9000.0,
        'pesticides': 2500.0,
        'labor': 16000.0,
        'irrigation_power': 6000.0,
        'machinery_rental': 5000.0
    },
    'Soybean': {
        'seeds': 2200.0,
        'fertilizers': 3200.0,
        'pesticides': 2000.0,
        'labor': 4000.0,
        'irrigation_power': 1500.0,
        'machinery_rental': 2800.0
    },
    'Maize / Corn': {
        'seeds': 2500.0,
        'fertilizers': 4000.0,
        'pesticides': 2200.0,
        'labor': 5000.0,
        'irrigation_power': 2000.0,
        'machinery_rental': 3000.0
    },
    'Onion': {
        'seeds': 3500.0,
        'fertilizers': 6000.0,
        'pesticides': 4500.0,
        'labor': 12000.0,
        'irrigation_power': 3000.0,
        'machinery_rental': 2800.0
    }
}

# Average Yield Benchmarks (Quintals / Acre)
CROP_YIELD_BENCHMARKS: Dict[str, float] = {
    'Cotton': 12.0,
    'Wheat': 20.0,
    'Rice / Paddy': 24.0,
    'Tomato': 150.0,
    'Sugarcane': 380.0,
    'Soybean': 10.0,
    'Maize / Corn': 24.0,
    'Onion': 110.0
}

# Mandi & MSP Benchmarks (INR / Quintal)
CROP_PRICE_BENCHMARKS: Dict[str, Dict[str, Any]] = {
    'Cotton': {'mandi_price': 7350.0, 'msp': 7121.0, 'trend': 'Rising 📈'},
    'Wheat': {'mandi_price': 2450.0, 'msp': 2275.0, 'trend': 'Stable ⚖️'},
    'Rice / Paddy': {'mandi_price': 2380.0, 'msp': 2300.0, 'trend': 'Stable ⚖️'},
    'Tomato': {'mandi_price': 1850.0, 'msp': 1600.0, 'trend': 'Rising 📈'},
    'Sugarcane': {'mandi_price': 355.0, 'msp': 340.0, 'trend': 'Stable ⚖️'},
    'Soybean': {'mandi_price': 4950.0, 'msp': 4892.0, 'trend': 'Falling 📉'},
    'Maize / Corn': {'mandi_price': 2320.0, 'msp': 2225.0, 'trend': 'Rising 📈'},
    'Onion': {'mandi_price': 2400.0, 'msp': 2000.0, 'trend': 'Rising 📈'}
}

def calculate_farm_economics(
    crop_name: str = 'Cotton',
    variety: str = 'Standard Hybrid',
    farm_size_acres: float = 2.0,
    custom_yield_qtl_per_acre: Optional[float] = None,
    custom_mandi_price: Optional[float] = None,
    custom_costs: Optional[Dict[str, float]] = None
) -> EconomicsReport:
    """Calculates comprehensive farm profitability, break-even, and marketing advice."""
    
    # 1. Cost Calculations
    base_costs = CROP_COST_BENCHMARKS.get(crop_name, CROP_COST_BENCHMARKS.get('Cotton'))
    costs_dict = custom_costs if custom_costs else base_costs

    seed_c = costs_dict.get('seeds', base_costs['seeds'])
    fert_c = costs_dict.get('fertilizers', base_costs['fertilizers'])
    pest_c = costs_dict.get('pesticides', base_costs['pesticides'])
    labor_c = costs_dict.get('labor', base_costs['labor'])
    irr_c = costs_dict.get('irrigation_power', base_costs['irrigation_power'])
    mach_c = costs_dict.get('machinery_rental', base_costs['machinery_rental'])

    cost_items = [
        CostItem(category="Quality Certified Seeds", per_acre_inr=seed_c, amount_inr=seed_c * farm_size_acres, description="High-germination hybrid seeds & seed treatment"),
        CostItem(category="Chemical & Organic Fertilizers", per_acre_inr=fert_c, amount_inr=fert_c * farm_size_acres, description="Basal DAP, Urea, MOP & Farm Yard Manure (FYM)"),
        CostItem(category="Plant Protection & Pesticides", per_acre_inr=pest_c, amount_inr=pest_c * farm_size_acres, description="Insecticides, fungicides & bio-pesticide sprays"),
        CostItem(category="Field Labor & Operations", per_acre_inr=labor_c, amount_inr=labor_c * farm_size_acres, description="Ploughing, manual weeding, spraying, and harvest picking"),
        CostItem(category="Irrigation & Electricity / Fuel", per_acre_inr=irr_c, amount_inr=irr_c * farm_size_acres, description="Drip fertigation & pump operating power"),
        CostItem(category="Machinery, Tractor & Rental", per_acre_inr=mach_c, amount_inr=mach_c * farm_size_acres, description="Rotavator, tractor tilling, and post-harvest threshing")
    ]

    total_cost = sum(item.amount_inr for item in cost_items)

    # 2. Yield Calculations
    yield_per_acre = custom_yield_qtl_per_acre or CROP_YIELD_BENCHMARKS.get(crop_name, 12.0)
    total_yield = round(yield_per_acre * farm_size_acres, 1)

    # 3. Market Pricing & Revenue
    price_info = CROP_PRICE_BENCHMARKS.get(crop_name, CROP_PRICE_BENCHMARKS.get('Cotton'))
    mandi_price = custom_mandi_price or price_info['mandi_price']
    msp_price = price_info['msp']
    trend = price_info['trend']

    gross_revenue = round(total_yield * mandi_price, 2)
    net_profit = round(gross_revenue - total_cost, 2)
    roi_pct = round((net_profit / total_cost) * 100.0, 1) if total_cost > 0 else 0.0

    prod_cost_per_qtl = round(total_cost / total_yield, 1) if total_yield > 0 else 0.0
    breakeven_price = prod_cost_per_qtl

    # 4. Market Advisory Intelligence
    if mandi_price >= msp_price * 1.05:
        advisory = (
            f"Current Mandi price of ₹{mandi_price:,.0f}/Q is above government MSP (₹{msp_price:,.0f}/Q). "
            f"Price trend is {trend}. Recommendation: Strong local market demand. Stagger produce sales in 2 lots over the next 15-20 days."
        )
    elif mandi_price >= msp_price:
        advisory = (
            f"Current Mandi price of ₹{mandi_price:,.0f}/Q matches MSP closely (₹{msp_price:,.0f}/Q). "
            f"Trend is {trend}. Recommendation: Register at nearest government procurement center (PACS/NAFED) as guaranteed safety floor."
        )
    else:
        advisory = (
            f"Mandi price (₹{mandi_price:,.0f}/Q) is currently lagging below MSP (₹{msp_price:,.0f}/Q). "
            f"Recommendation: Sell produce strictly at official MSP procurement center or hold in certified warehouse (WDRA) to take advantage of upcoming price rebound."
        )

    return EconomicsReport(
        crop_name=crop_name,
        variety=variety,
        farm_size_acres=farm_size_acres,
        expected_yield_per_acre_qtl=yield_per_acre,
        total_expected_yield_qtl=total_yield,
        current_mandi_price_per_qtl=mandi_price,
        msp_benchmark_price_per_qtl=msp_price,
        price_trend=trend,
        gross_revenue_inr=gross_revenue,
        total_cost_inr=total_cost,
        net_profit_inr=net_profit,
        roi_percentage=roi_pct,
        production_cost_per_qtl=prod_cost_per_qtl,
        breakeven_price_per_qtl=breakeven_price,
        costs_breakdown=cost_items,
        market_selling_advisory=advisory
    )

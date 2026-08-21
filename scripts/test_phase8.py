import sys
sys.path.insert(0, ".")
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

print("=== TESTING PHASE 8: FARM ECONOMICS & PROFIT CALCULATOR API ===")

# 1. Test GET /api/economics/report
r1 = client.get("/api/economics/report")
print("1. GET /api/economics/report -> Status:", r1.status_code)
assert r1.status_code == 200
data1 = r1.json()
print("   - Crop:", data1["crop_name"], "| Size:", data1["farm_size_acres"], "Acres")
print("   - Yield Total:", data1["total_expected_yield_qtl"], "Qtl")
print("   - Gross Revenue: ₹", data1["gross_revenue_inr"], "| Total Cost: ₹", data1["total_cost_inr"])
print("   - Net Profit: ₹", data1["net_profit_inr"], "| ROI:", data1["roi_percentage"], "%")
print("   - Mandi Price: ₹", data1["current_mandi_price_per_qtl"], "/Q | MSP: ₹", data1["msp_benchmark_price_per_qtl"], "/Q")
print("   - Break-Even: ₹", data1["breakeven_price_per_qtl"], "/Q")
assert data1["gross_revenue_inr"] > data1["total_cost_inr"]
assert len(data1["costs_breakdown"]) == 6

# 2. Test POST /api/economics/calculate-custom
payload = {
    "crop_name": "Tomato",
    "variety": "Abhinav Hybrid",
    "farm_size": 2.0,
    "custom_yield_qtl_per_acre": 160.0,
    "custom_mandi_price": 2000.0,
    "custom_costs": {
        "seeds": 5000.0,
        "fertilizers": 8000.0,
        "pesticides": 7000.0,
        "labor": 15000.0,
        "irrigation_power": 4000.0,
        "machinery_rental": 3500.0
    }
}
r2 = client.post("/api/economics/calculate-custom", json=payload)
print("2. POST /api/economics/calculate-custom -> Status:", r2.status_code)
assert r2.status_code == 200
data2 = r2.json()
print("   - Custom Crop:", data2["crop_name"], "| Yield:", data2["total_expected_yield_qtl"], "Qtl")
print("   - Revenue: ₹", data2["gross_revenue_inr"], "| Cost: ₹", data2["total_cost_inr"])
print("   - Net Profit: ₹", data2["net_profit_inr"], "| ROI:", data2["roi_percentage"], "%")
assert data2["total_expected_yield_qtl"] == 320.0  # 160 * 2
assert data2["gross_revenue_inr"] == 640000.0  # 320 * 2000
assert data2["total_cost_inr"] == 85000.0  # 42500 * 2
assert data2["net_profit_inr"] == 555000.0

print("=== ALL PHASE 8 TESTS PASSED SUCCESSFULLY! ===")

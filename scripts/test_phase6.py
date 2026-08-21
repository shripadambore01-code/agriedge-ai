import sys
sys.path.insert(0, ".")
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

print("=== TESTING PHASE 6: PRECISION IRRIGATION ADVISOR API ===")

# 1. Test GET /api/irrigation/advisor with normal soil feel
r1 = client.get("/api/irrigation/advisor?soil_feel=slightly_moist")
print("1. GET /api/irrigation/advisor -> Status:", r1.status_code)
assert r1.status_code == 200
data1 = r1.json()
print("   - Action:", data1["action_type"], "| Headline:", data1["action_headline"])
print("   - Run-Time:", data1["recommended_runtime_formatted"], "| Water:", data1["total_water_litres"], "L")
print("   - Daily ETc:", data1["daily_etc_mm"], "mm | Kc:", data1["kc_factor"])
assert "Litres" not in str(data1["total_water_litres"])  # Should be integer
assert data1["kc_factor"] > 0

# 2. Test Custom Irrigation calculation with rain forecast (Expect SKIP_IRRIGATION)
payload = {
    "crop_name": "Cotton",
    "sowing_date": "2026-07-15",
    "farm_size": 3.0,
    "soil_type": "Black Cotton / Heavy Clay",
    "irrigation_method": "Drip Irrigation",
    "soil_feel": "slightly_moist",
    "reference_et0_mm": 5.0,
    "forecast_rain_24h_mm": 15.0
}
r2 = client.post("/api/irrigation/calculate-custom", json=payload)
print("2. POST /api/irrigation/calculate-custom (Rain scenario) -> Status:", r2.status_code)
assert r2.status_code == 200
data2 = r2.json()
print("   - Action:", data2["action_type"])
print("   - Headline:", data2["action_headline"])
print("   - Run-Time:", data2["recommended_runtime_formatted"], "(Expected 0 for rain)")
assert data2["action_type"] == "SKIP_IRRIGATION"
assert data2["total_water_litres"] == 0

# 3. Test dry cracked soil scenario (Higher water delivery)
payload3 = {
    "crop_name": "Tomato",
    "sowing_date": "2026-07-15",
    "farm_size": 1.5,
    "soil_type": "Loamy Soil",
    "irrigation_method": "Drip Irrigation",
    "soil_feel": "dry_cracked",
    "reference_et0_mm": 5.2,
    "forecast_rain_24h_mm": 0.0
}
r3 = client.post("/api/irrigation/calculate-custom", json=payload3)
print("3. POST /api/irrigation/calculate-custom (Dry soil) -> Status:", r3.status_code)
assert r3.status_code == 200
data3 = r3.json()
print("   - Action:", data3["action_type"])
print("   - Run-Time:", data3["recommended_runtime_formatted"])
print("   - Total Water:", data3["total_water_litres"], "L")
assert data3["total_water_litres"] > 0
assert data3["soil_depletion_pct"] == 75

print("=== ALL PHASE 6 TESTS PASSED SUCCESSFULLY! ===")

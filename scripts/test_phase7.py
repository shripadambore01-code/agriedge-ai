import sys
sys.path.insert(0, ".")
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

print("=== TESTING PHASE 7: SOIL HEALTH CARD & FERTILIZER ENGINE API ===")

# 1. Test GET /api/soil/recommendation with standard_black preset
r1 = client.get("/api/soil/recommendation?preset=standard_black")
print("1. GET /api/soil/recommendation -> Status:", r1.status_code)
assert r1.status_code == 200
data1 = r1.json()
print("   - Crop:", data1["crop_name"], "| Farm Size:", data1["farm_size_acres"], "Acres")
print("   - Urea Bags (45kg):", data1["total_urea_bags_45kg"], "| DAP Bags (50kg):", data1["total_dap_bags_50kg"])
print("   - MOP Bags (50kg):", data1["total_mop_bags_50kg"])
print("   - Zinc Sulphate:", data1["zinc_sulphate_total_kg"], "kg | Borax:", data1["borax_total_kg"], "kg")
print("   - Splits Count:", len(data1["splits"]))
assert data1["total_urea_bags_45kg"] > 0
assert data1["total_dap_bags_50kg"] > 0
assert len(data1["splits"]) == 3

# 2. Test POST /api/soil/calculate with custom test values (Degraded soil test)
payload = {
    "crop_name": "Wheat",
    "farm_size": 4.0,
    "ph": 6.2,
    "oc_pct": 0.35,
    "n_kg_ha": 150.0,
    "p_kg_ha": 10.0,
    "k_kg_ha": 110.0,
    "zn_ppm": 0.40,
    "b_ppm": 0.30
}
r2 = client.post("/api/soil/calculate", json=payload)
print("2. POST /api/soil/calculate -> Status:", r2.status_code)
assert r2.status_code == 200
data2 = r2.json()
print("   - Crop:", data2["crop_name"], "| Size:", data2["farm_size_acres"], "Acres")
print("   - Urea Bags:", data2["total_urea_bags_45kg"], "| DAP Bags:", data2["total_dap_bags_50kg"])
print("   - Zn Required:", data2["zinc_sulphate_total_kg"], "kg (Expected 40kg for 4 acres)")
print("   - Organic Manure:", data2["organic_manure_tonnes"], "Tonnes")
assert data2["zinc_sulphate_total_kg"] == 40.0
assert data2["borax_total_kg"] == 8.0
assert "Deficient" in data2["zinc_status"]

print("=== ALL PHASE 7 TESTS PASSED SUCCESSFULLY! ===")

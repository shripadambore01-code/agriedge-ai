import sys
sys.path.insert(0, ".")
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

print("=== TESTING PHASE 9: GOVT SCHEMES & SUBSIDY ASSISTANT API ===")

# 1. Test GET /api/schemes/matched
r1 = client.get("/api/schemes/matched")
print("1. GET /api/schemes/matched -> Status:", r1.status_code)
assert r1.status_code == 200
data1 = r1.json()
print("   - Farmer:", data1["farmer_name"], "| Category:", data1["farmer_category"])
print("   - Matched Schemes Count:", data1["matched_count"])
print("   - Total Potential Benefit: ₹", data1["total_potential_benefit_inr"])
assert data1["matched_count"] >= 5
assert data1["total_potential_benefit_inr"] > 100000.0

scheme_names = [s["name"] for s in data1["matched_schemes"]]
print("   - Schemes List:", [s.split(" (")[0] for s in scheme_names])
assert any("PM-KISAN" in name for name in scheme_names)
assert any("PMFBY" in name for name in scheme_names)
assert any("PM-KUSUM" in name for name in scheme_names)

# Check document checklist in first scheme
s0 = data1["matched_schemes"][0]
assert len(s0["required_documents"]) >= 3
assert len(s0["how_to_apply"]) >= 2
assert s0["official_portal_url"].startswith("http")

# 2. Test POST /api/schemes/check with custom parameters
payload = {
    "farmer_name": "Ramesh Patil",
    "location": "Nashik, Maharashtra",
    "farm_size": 1.5,
    "crop_name": "Tomato",
    "irrigation_method": "Drip Irrigation"
}
r2 = client.post("/api/schemes/check", json=payload)
print("2. POST /api/schemes/check -> Status:", r2.status_code)
assert r2.status_code == 200
data2 = r2.json()
print("   - Farmer:", data2["farmer_name"], "| Category:", data2["farmer_category"])
print("   - Total Potential Benefit: ₹", data2["total_potential_benefit_inr"])
assert "Marginal" in data2["farmer_category"]

print("=== ALL PHASE 9 TESTS PASSED SUCCESSFULLY! ===")

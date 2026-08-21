import sys
sys.path.insert(0, '.')
from fastapi.testclient import TestClient
from backend.main import app
import io

client = TestClient(app)

print("=== TESTING PHASE 5: AI CROP DOCTOR API ===")

# 1. Test Symptom-based diagnosis (Offline decision tree)
payload = {
    "crop_name": "Cotton",
    "symptom_key": "pink_bollworm",
    "additional_notes": "Observed exit holes on green bolls",
    "language": "en"
}
r1 = client.post("/api/doctor/diagnose-symptoms", json=payload)
print("1. POST /api/doctor/diagnose-symptoms -> Status:", r1.status_code)
assert r1.status_code == 200
data1 = r1.json()
print("   - Disease:", data1["disease_name"], f"({data1['scientific_name']})")
print("   - Severity:", data1["severity"], "| Confidence:", data1["confidence_pct"], "%")
print("   - 24h Action:", data1["immediate_action_24h"])
print("   - Chemical:", data1["chemical_treatment"], "| Dosage/L:", data1["chemical_dosage_per_liter"])
print("   - Organic:", data1["organic_treatment"])
assert "Pink Bollworm" in data1["disease_name"]
assert len(data1["preventive_measures"]) >= 2

# 2. Test Image Upload diagnosis
dummy_img = io.BytesIO(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xff\xd9")

r2 = client.post(
    "/api/doctor/diagnose-image",
    files={"image": ("leaf.jpg", dummy_img, "image/jpeg")},
    data={"crop_name": "Wheat", "symptoms": "Yellow stripes", "language": "en"}
)
print("2. POST /api/doctor/diagnose-image -> Status:", r2.status_code)
assert r2.status_code == 200
data2 = r2.json()
print("   - Image Disease:", data2["disease_name"])
print("   - Mode Used:", data2["mode_used"])
assert "disease_name" in data2
assert "chemical_treatment" in data2

print("=== ALL PHASE 5 TESTS PASSED SUCCESSFULLY! ===")

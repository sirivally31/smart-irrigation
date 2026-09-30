import sys
import os
sys.path.insert(0, os.path.abspath("."))

import pytest
from fastapi.testclient import TestClient
from src.api.app import app
from src.db.database import init_db

init_db()
client = TestClient(app)

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"
    assert res.json()["models_loaded"] is True

def test_predict_preserved():
    payload = {
        "field_id": "north",
        "crop_type": "tomato",
        "growth_stage": "vegetative",
        "soil_moisture_pct": 28.0,
        "temperature_c": 26.0,
        "humidity_pct": 55.0,
        "rainfall_mm": 0.0,
        "wind_speed_mps": 2.0,
        "solar_radiation_wm2": 520.0,
        "days_since_irrigation": 3,
        "forecast_rainfall_mm": 0.0,
        "previous_irrigation_liters": 20.0
    }
    res = client.post("/predict", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "irrigation_needed" in data
    assert "water_quantity_liters" in data
    assert "duration_minutes" in data

def test_fields_crud():
    res = client.get("/api/fields")
    assert res.status_code == 200
    fields = res.json()
    assert len(fields) >= 4
    field_ids = [f["id"] for f in fields]
    assert "north" in field_ids

    # Field detail
    res_north = client.get("/api/fields/north")
    assert res_north.status_code == 200
    assert res_north.json()["crop_type"] == "tomato"

def test_today_recommendations():
    res = client.get("/api/recommendations/today")
    assert res.status_code == 200
    schedules = res.json()
    assert isinstance(schedules, list)

def test_alerts_and_evaluation():
    res_eval = client.post("/api/alerts/evaluate")
    assert res_eval.status_code == 200

    res_alerts = client.get("/api/alerts")
    assert res_alerts.status_code == 200
    alerts = res_alerts.json()
    assert len(alerts) > 0

    stats = client.get("/api/alerts/stats").json()
    assert "unread" in stats

def test_ai_multilingual():
    for lang in ["en", "hi", "kn"]:
        res = client.post("/api/ai/explain", json={"field_id": "north", "language": lang})
        assert res.status_code == 200
        data = res.json()
        assert "headline" in data
        assert "explanation" in data
        assert len(data["explanation"]) > 10

def test_ai_voice_query():
    res_en = client.post("/api/ai/voice-query", json={"query": "Should I water my tomatoes today?", "language": "en"})
    assert res_en.status_code == 200
    assert "answer" in res_en.json()

    res_kn = client.post("/api/ai/voice-query", json={"query": "ಇಂದು ನೀರು ಹಾಕಬೇಕೇ?", "language": "kn"})
    assert res_kn.status_code == 200
    assert "answer" in res_kn.json()

def test_reports():
    res_pdf = client.get("/api/reports/pdf?field_id=north&days=7")
    assert res_pdf.status_code == 200
    assert res_pdf.headers["content-type"] == "application/pdf"
    assert len(res_pdf.content) > 1000

    res_csv = client.get("/api/reports/csv?type=irrigation")
    assert res_csv.status_code == 200
    assert "record_id" in res_csv.text

def test_notification_tests():
    res_push = client.post("/api/notifications/push/test")
    assert res_push.status_code == 200

    res_sms = client.post("/api/notifications/sms/test")
    assert res_sms.status_code == 200

    res_email = client.post("/api/notifications/email/test")
    assert res_email.status_code == 200

if __name__ == "__main__":
    print("Running tests directly...")
    test_health()
    print("[OK] Health check passed")
    test_predict_preserved()
    print("[OK] Prediction check passed")
    test_fields_crud()
    print("[OK] Fields CRUD passed")
    test_today_recommendations()
    print("[OK] Recommendations passed")
    test_alerts_and_evaluation()
    print("[OK] Alerts & evaluation passed")
    test_ai_multilingual()
    print("[OK] AI Multilingual (EN, HI, KN) passed")
    test_ai_voice_query()
    print("[OK] AI Voice Query passed")
    test_reports()
    print("[OK] PDF & CSV reports passed")
    test_notification_tests()
    print("[OK] Notifications passed")
    print("All backend tests PASSED successfully!")

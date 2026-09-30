import os
import requests
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from src.db.models import Field, SensorReading, IrrigationSchedule, Alert
from src.services.ml_service import predict_for_field

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "")
SARVAM_API_URL = os.getenv("SARVAM_API_URL", "https://api.sarvam.ai")


# --- SARVAM AI / MULTILINGUAL EXPLANATION SERVICE ---
def explain_recommendation(
    field_id: str,
    language: str,
    db: Session
) -> Dict[str, Any]:
    """
    Explain the ML irrigation recommendation in simple farmer language (EN, HI, KN).
    Calls Sarvam AI if configured; otherwise uses high-quality domain fallback.
    """
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        return {"error": "Field not found"}

    # Get ML prediction
    try:
        pred = predict_for_field(db, field_id)
    except Exception as e:
        pred = {
            "irrigation_needed": False,
            "water_quantity_liters": 0.0,
            "duration_minutes": 0.0,
            "reason": "Unable to calculate ML prediction"
        }

    latest_sensor = db.query(SensorReading).filter(
        SensorReading.field_id == field_id
    ).order_by(SensorReading.timestamp.desc()).first()

    moisture = round(latest_sensor.soil_moisture_pct, 1) if latest_sensor else 35.0
    crop = field.crop_type.capitalize()
    stage = field.growth_stage.capitalize()

    # If Sarvam AI key is configured, invoke Sarvam translation/completion
    if SARVAM_API_KEY and not SARVAM_API_KEY.startswith("your_"):
        try:
            prompt = (
                f"Explain this irrigation recommendation to an Indian farmer in simple {language} language:\n"
                f"Crop: {crop}, Growth stage: {stage}, Current soil moisture: {moisture}%.\n"
                f"Recommendation: Irrigation needed = {pred['irrigation_needed']}, Water quantity = {pred['water_quantity_liters']} Liters, "
                f"Duration = {pred['duration_minutes']} minutes. Reason: {pred['reason']}."
            )
            resp = requests.post(
                f"{SARVAM_API_URL}/v1/chat/completions",
                headers={"Authorization": f"Bearer {SARVAM_API_KEY}", "Content-Type": "application/json"},
                json={"model": "sarvam-2b", "messages": [{"role": "user", "content": prompt}], "temperature": 0.3},
                timeout=5
            )
            if resp.status_code == 200:
                content = resp.json()["choices"][0]["message"]["content"]
                return {
                    "field_id": field_id,
                    "language": language,
                    "headline": f"AI Recommendation for {crop}",
                    "explanation": content,
                    "farmer_tip": "Apply water in early morning or late evening for minimum evaporation.",
                    "source": "sarvam_ai"
                }
        except Exception as e:
            print(f"[Sarvam AI Error -> Falling back to domain generator] {e}")

    # --- INTELLIGENT DOMAIN MULTILINGUAL GENERATOR ---
    needed = pred["irrigation_needed"]
    qty = pred["water_quantity_liters"]
    dur = pred["duration_minutes"]

    if language == "hi":  # Hindi
        if needed:
            headline = f"{crop} के लिए सिंचाई आवश्यक है"
            explanation = (
                f"वर्तमान में आपके {crop} के खेत में मिट्टी की नमी {moisture}% है। "
                f"पौधों की {stage} अवस्था के लिए यह कम है। "
                f"मॉडल आपको {qty} लीटर पानी {dur} मिनट तक देने की सलाह देता है।"
            )
            tip = "सुबह के समय ड्रिप सिंचाई करने से 30% तक पानी की बचत होती है।"
        else:
            headline = f"{crop} में आज सिंचाई की आवश्यकता नहीं है"
            explanation = (
                f"मिट्टी में पर्याप्त नमी ({moisture}%) उपलब्ध है। "
                f"वर्तमान मौसम और वाष्पीकरण को देखते हुए अभी अतिरिक्त पानी देने से जड़ों को नुकसान हो सकता है।"
            )
            tip = "दोपहर के समय नमी की पुनः जांच करें।"

    elif language == "kn":  # Kannada
        if needed:
            headline = f"{crop} ಬೆಳೆಗೆ ನೀರಾವರಿ ಅಗತ್ಯವಿದೆ"
            explanation = (
                f"ಪ್ರಸ್ತುತ ನಿಮ್ಮ {crop} ಜಮೀನಿನಲ್ಲಿ ಮಣ್ಣಿನ ತೇವಾಂಶ {moisture}% ಇದೆ. "
                f"ಬೆಳೆಯ {stage} ಹಂತಕ್ಕೆ ಇದು ಕಡಿಮೆಯಾಗಿದೆ. "
                f"ಬುದ್ಧಿವಂತ ನೀರಾವರಿ ವ್ಯವಸ್ಥೆಯು {dur} ನಿಮಿಷಗಳ ಕಾಲ {qty} ಲೀಟರ್ ನೀರುಣಿಸಲು ಶಿಫಾರಸು ಮಾಡುತ್ತದೆ."
            )
            tip = "ಮುಂಜಾನೆ ಅಥವಾ ಸಂಜೆ ವೇಳೆ ನೀರುಣಿಸುವುದರಿಂದ ನೀರಿನ ಆವಿಯಾಗುವಿಕೆ ತಡೆಯಬಹುದು."
        else:
            headline = f"{crop} ಬೆಳೆಗೆ ಇಂದು ನೀರಾವರಿ ಅಗತ್ಯವಿಲ್ಲ"
            explanation = (
                f"ನಿಮ್ಮ ಹೊಲದ ಮಣ್ಣಿನಲ್ಲಿ ಸಮರ್ಪಕ ತೇವಾಂಶ ({moisture}%) ಇದೆ. "
                f"ಈಗ ನೀರು ಹರಿಸುವುದರಿಂದ ಬೇರುಗಳಿಗೆ ಹಾನಿಯಾಗಬಹುದು ಮತ್ತು ಪೋಷಕಾಂಶಗಳು ಸೋರಿಹೋಗಬಹುದು."
            )
            tip = "ಮಳೆಯ ಮುನ್ಸೂಚನೆಯನ್ನು ಗಮನದಲ್ಲಿಟ್ಟುಕೊಂಡು ಮುಂದಿನ ನಿರ್ಧಾರ ತೆಗೆದುಕೊಳ್ಳಿ."

    else:  # English
        if needed:
            headline = f"Irrigation Recommended for {crop}"
            explanation = (
                f"Current soil moisture in your {crop} plot is {moisture}%, which is below the optimal threshold for the {stage} stage. "
                f"The AI model recommends applying {qty} Liters over a {dur}-minute cycle."
            )
            tip = "Irrigate during early morning or late evening hours to minimize evapotranspiration losses."
        else:
            headline = f"No Irrigation Required for {crop}"
            explanation = (
                f"Soil moisture is healthy at {moisture}%. Weather conditions and soil retention currently fulfill crop evapotranspiration demand. "
                f"Additional watering may cause waterlogging."
            )
            tip = "Monitor forecast rainfall before scheduling the next cycle."

    return {
        "field_id": field_id,
        "language": language,
        "headline": headline,
        "explanation": explanation,
        "farmer_tip": tip,
        "source": "domain_expert"
    }


# --- CONVERSATIONAL VOICE QUERY PROCESSOR ---
def process_voice_query(
    query: str,
    language: str,
    db: Session,
    field_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Process farmer voice query in EN, HI, or KN, pulling real field data and ML predictions.
    """
    query_lower = query.lower()

    # Identify field if mentioned or provided
    all_fields = db.query(Field).all()
    target_field = None
    if field_id:
        target_field = db.query(Field).filter(Field.id == field_id).first()
    else:
        for f in all_fields:
            if f.id in query_lower or f.crop_type in query_lower or f.name.lower() in query_lower:
                target_field = f
                break

    if not target_field and all_fields:
        target_field = all_fields[0]  # default to first field (e.g. North - Tomato)

    # Fetch context data
    latest_reading = db.query(SensorReading).filter(
        SensorReading.field_id == target_field.id
    ).order_by(SensorReading.timestamp.desc()).first()

    pred = predict_for_field(db, target_field.id)
    moisture = round(latest_reading.soil_moisture_pct, 1) if latest_reading else 34.0
    crop = target_field.crop_type.capitalize()

    # Active alerts
    unread_alerts = db.query(Alert).filter(Alert.status == "unread").count()

    # Generate answer based on query intent & language
    if language == "kn":  # Kannada
        if "ನೀರ" in query or "ನೀರು" in query or "water" in query_lower or "irrigate" in query_lower:
            if pred["irrigation_needed"]:
                answer = (
                    f"ಹೌದು, {crop} ಜಮೀನಿನಲ್ಲಿ ತೇವಾಂಶ {moisture}% ಇದೆ. "
                    f"ಮಾದರಿಯು {pred['duration_minutes']} ನಿಮಿಷಗಳ ಕಾಲ {pred['water_quantity_liters']} ಲೀಟರ್ ನೀರುಣಿಸಲು ಶಿಫಾರಸು ಮಾಡುತ್ತದೆ."
                )
            else:
                answer = f"ಇಲ್ಲ, ನಿಮ್ಮ {crop} ಜಮೀನಿನಲ್ಲಿ ತೇವಾಂಶ {moisture}% ಇದೆ. ಇಂದು ನೀರುಣಿಸುವ ಅಗತ್ಯವಿಲ್ಲ."
        elif "ತೇವಾಂಶ" in query or "moisture" in query_lower or "soil" in query_lower:
            answer = f"{target_field.name} ನಲ್ಲಿ ಪ್ರಸ್ತುತ ಮಣ್ಣಿನ ತೇವಾಂಶ {moisture}% ಆಗಿದೆ."
        elif "ಎಚ್ಚರಿಕೆ" in query or "alert" in query_lower:
            answer = f"ನಿಮ್ಮ ತೋಟದಲ್ಲಿ ಪ್ರಸ್ತುತ {unread_alerts} ಸಕ್ರಿಯ ಎಚ್ಚರಿಕೆಗಳಿವೆ. ದಯವಿಟ್ಟು ಎಚ್ಚರಿಕೆಗಳ ಪುಟವನ್ನು ಪರಿಶೀಲಿಸಿ."
        else:
            answer = (
                f"{target_field.name} ನಲ್ಲಿ ಮಣ್ಣಿನ ತೇವಾಂಶ {moisture}% ಇದೆ. "
                f"{'ನೀರುಣಿಸಲು ಶಿಫಾರಸು ಮಾಡಲಾಗಿದೆ' if pred['irrigation_needed'] else 'ಸದ್ಯಕ್ಕೆ ನೀರುಣಿಸುವ ಅಗತ್ಯವಿಲ್ಲ'}."
            )

    elif language == "hi":  # Hindi
        if "पानी" in query or "सिंचाई" in query or "water" in query_lower or "irrigate" in query_lower:
            if pred["irrigation_needed"]:
                answer = (
                    f"हाँ, {crop} के खेत में नमी {moisture}% है। "
                    f"मॉडल {pred['duration_minutes']} मिनट के लिए {pred['water_quantity_liters']} लीटर पानी देने की सलाह देता है।"
                )
            else:
                answer = f"नहीं, आपके {crop} के खेत में {moisture}% पर्याप्त नमी है। आज पानी देने की आवश्यकता नहीं है।"
        elif "नमी" in query or "moisture" in query_lower or "soil" in query_lower:
            answer = f"{target_field.name} में वर्तमान मिट्टी की नमी {moisture}% है।"
        elif "अलर्ट" in query or "चेतावनी" in query or "alert" in query_lower:
            answer = f"आपके खेत के लिए वर्तमान में {unread_alerts} सक्रिय अलर्ट हैं।"
        else:
            answer = (
                f"{target_field.name} में मिट्टी की नमी {moisture}% है। "
                f"{'सिंचाई की सिफारिश की गई है' if pred['irrigation_needed'] else 'आज सिंचाई की आवश्यकता नहीं है'}."
            )

    else:  # English
        if "water" in query_lower or "irrigate" in query_lower or "should" in query_lower:
            if pred["irrigation_needed"]:
                answer = (
                    f"Yes, soil moisture in your {crop} field is {moisture}%. "
                    f"The ML model recommends irrigating for {pred['duration_minutes']} minutes ({pred['water_quantity_liters']} Liters)."
                )
            else:
                answer = (
                    f"No, soil moisture in your {crop} field is adequate at {moisture}%. "
                    f"No irrigation is required today."
                )
        elif "moisture" in query_lower or "sensor" in query_lower:
            answer = f"Current soil moisture in {target_field.name} is {moisture}% with temperature at {round(latest_reading.temperature_c, 1) if latest_reading else 26}°C."
        elif "alert" in query_lower or "warning" in query_lower:
            answer = f"You have {unread_alerts} unread alert(s). Check the Alerts tab for actionable details."
        else:
            answer = (
                f"For {target_field.name}: Soil moisture is {moisture}%. "
                f"Today's irrigation recommendation: {'Irrigation needed' if pred['irrigation_needed'] else 'No watering needed'}."
            )

    return {
        "query": query,
        "language": language,
        "answer": answer,
        "relevant_fields": [target_field.id],
        "source": "domain_ai_agent"
    }

from datetime import datetime, timedelta
from typing import List
from sqlalchemy.orm import Session
from src.db.models import Field, SensorReading, IrrigationSchedule, Alert, NotificationPreference
from src.services.ml_service import predict_for_field
from src.services.notification_service import dispatch_alert_notifications

COOLDOWN_HOURS = 6


def is_duplicate_alert(db: Session, field_id: str, alert_type: str) -> bool:
    """Check if an active/recent alert of the same type was created within COOLDOWN_HOURS."""
    threshold_time = datetime.utcnow() - timedelta(hours=COOLDOWN_HOURS)
    existing = db.query(Alert).filter(
        Alert.field_id == field_id,
        Alert.alert_type == alert_type,
        Alert.status.in_(["unread", "read"]),
        Alert.created_at >= threshold_time
    ).first()
    return existing is not None


def evaluate_field_alerts(db: Session, field: Field) -> List[Alert]:
    """Run rule-based checks and ML checks for a specific field, generating alerts if triggered."""
    generated_alerts = []

    # Get farmer notification preferences
    prefs = db.query(NotificationPreference).first()
    low_thresh = prefs.low_moisture_threshold if prefs else (field.target_moisture_min or 30.0)
    rain_thresh = prefs.high_rain_threshold if prefs else 15.0

    # Get latest sensor reading
    latest_sensor = db.query(SensorReading).filter(
        SensorReading.field_id == field.id
    ).order_by(SensorReading.timestamp.desc()).first()

    now = datetime.utcnow()

    # Rule 1: Stale Data / Sensor Failure Check
    if not latest_sensor:
        if not is_duplicate_alert(db, field.id, "sensor_failure"):
            alert = Alert(
                field_id=field.id,
                alert_type="sensor_failure",
                severity="warning",
                title=f"No Sensor Data: {field.name}",
                message=f"No sensor telemetry found for {field.name}. Check IoT gateway connectivity.",
                suggested_action="Verify field sensor power and telemetry transmission.",
                status="unread",
                created_at=now
            )
            db.add(alert)
            generated_alerts.append(alert)
    else:
        # Check staleness
        reading_age = now - latest_sensor.timestamp
        if reading_age > timedelta(hours=24):
            if not is_duplicate_alert(db, field.id, "stale_data"):
                alert = Alert(
                    field_id=field.id,
                    alert_type="stale_data",
                    severity="warning",
                    title=f"Stale Sensor Data: {field.name}",
                    message=f"Last sensor reading was {int(reading_age.total_seconds() // 3600)} hours ago ({latest_sensor.timestamp.strftime('%Y-%m-%d %H:%M')}).",
                    suggested_action="Inspect sensor batteries and solar harvester.",
                    status="unread",
                    created_at=now
                )
                db.add(alert)
                generated_alerts.append(alert)

        # Rule 2: Low Soil Moisture Check
        if latest_sensor.soil_moisture_pct < low_thresh:
            if not is_duplicate_alert(db, field.id, "low_moisture"):
                alert = Alert(
                    field_id=field.id,
                    alert_type="low_moisture",
                    severity="critical",
                    title=f"Critical Soil Moisture Deficit: {field.name}",
                    message=f"Current soil moisture is {round(latest_sensor.soil_moisture_pct, 1)}%, which is below threshold of {low_thresh}% for {field.crop_type} ({field.growth_stage}).",
                    suggested_action="Execute recommended irrigation schedule immediately to prevent crop wilting.",
                    status="unread",
                    created_at=now
                )
                db.add(alert)
                generated_alerts.append(alert)

        # Rule 3: Over-Watering Risk Check
        if latest_sensor.soil_moisture_pct > 80.0:
            if not is_duplicate_alert(db, field.id, "over_watering"):
                alert = Alert(
                    field_id=field.id,
                    alert_type="over_watering",
                    severity="warning",
                    title=f"Over-Watering Risk: {field.name}",
                    message=f"Soil moisture is saturated at {round(latest_sensor.soil_moisture_pct, 1)}%. Risk of root hypoxia and nutrient leaching.",
                    suggested_action="Pause all automated irrigation cycles and inspect drainage channels.",
                    status="unread",
                    created_at=now
                )
                db.add(alert)
                generated_alerts.append(alert)

        # Rule 4: Heavy Rainfall
        if latest_sensor.rainfall_mm >= rain_thresh:
            if not is_duplicate_alert(db, field.id, "heavy_rain"):
                alert = Alert(
                    field_id=field.id,
                    alert_type="heavy_rain",
                    severity="info",
                    title=f"Heavy Rainfall Detected: {field.name}",
                    message=f"Measured rainfall of {latest_sensor.rainfall_mm}mm on {field.name}. Irrigation schedule automatically suspended.",
                    suggested_action="No watering required. Natural rainfall satisfies crop evapotranspiration demand.",
                    status="unread",
                    created_at=now
                )
                db.add(alert)
                generated_alerts.append(alert)

    # Rule 5: ML-based Recommendation Deficit
    try:
        pred = predict_for_field(db, field.id)
        if pred["irrigation_needed"] and pred["water_quantity_liters"] >= 20.0:
            if not is_duplicate_alert(db, field.id, "ml_deficit"):
                alert = Alert(
                    field_id=field.id,
                    alert_type="ml_deficit",
                    severity="warning",
                    title=f"ML Predicted Irrigation Demand: {field.name}",
                    message=f"Smart Irrigation model recommends applying {pred['water_quantity_liters']}L ({pred['duration_minutes']} mins). {pred['reason']}",
                    suggested_action="Review Today's Irrigation Schedule and confirm valve activation.",
                    status="unread",
                    created_at=now
                )
                db.add(alert)
                generated_alerts.append(alert)
    except Exception:
        pass

    if generated_alerts:
        db.commit()
        for a in generated_alerts:
            db.refresh(a)
            # Dispatch notifications (Push, SMS, Email) according to farmer preferences
            try:
                dispatch_alert_notifications(db, a)
            except Exception as e:
                print(f"[Alert Engine] Notification dispatch failed: {e}")

    return generated_alerts


def evaluate_all_fields(db: Session) -> List[Alert]:
    """Evaluate alerts across all active fields."""
    fields = db.query(Field).filter(Field.is_active == True).all()
    all_generated = []
    for field in fields:
        alerts = evaluate_field_alerts(db, field)
        all_generated.extend(alerts)
    return all_generated

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.db.models import Field, Alert
from src.api.schemas import AlertResponse, AlertStatusUpdate
from src.services.alert_engine import evaluate_all_fields

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])


@router.get("", response_model=List[AlertResponse])
def get_alerts(
    field_id: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Retrieve all alerts with optional filtering."""
    query = db.query(Alert)

    if field_id:
        query = query.filter(Alert.field_id == field_id)
    if severity:
        query = query.filter(Alert.severity == severity)
    if status:
        query = query.filter(Alert.status == status)

    alerts = query.order_by(Alert.created_at.desc()).all()

    enriched = []
    for a in alerts:
        f = db.query(Field).filter(Field.id == a.field_id).first()
        enriched.append({
            "id": a.id,
            "field_id": a.field_id,
            "field_name": f.name if f else a.field_id.capitalize(),
            "alert_type": a.alert_type,
            "severity": a.severity,
            "title": a.title,
            "message": a.message,
            "suggested_action": a.suggested_action,
            "status": a.status,
            "created_at": a.created_at
        })
    return enriched


@router.post("/evaluate", response_model=List[AlertResponse])
def trigger_alert_evaluation(db: Session = Depends(get_db)):
    """Evaluate rule-based alert engine across all active fields."""
    new_alerts = evaluate_all_fields(db)
    enriched = []
    for a in new_alerts:
        f = db.query(Field).filter(Field.id == a.field_id).first()
        enriched.append({
            "id": a.id,
            "field_id": a.field_id,
            "field_name": f.name if f else a.field_id.capitalize(),
            "alert_type": a.alert_type,
            "severity": a.severity,
            "title": a.title,
            "message": a.message,
            "suggested_action": a.suggested_action,
            "status": a.status,
            "created_at": a.created_at
        })
    return enriched


@router.patch("/{alert_id}/status", response_model=AlertResponse)
def update_alert_status(
    alert_id: int,
    data: AlertStatusUpdate,
    db: Session = Depends(get_db)
):
    """Update status of an alert (mark as read or dismissed)."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found.")

    alert.status = data.status
    db.commit()
    db.refresh(alert)

    f = db.query(Field).filter(Field.id == alert.field_id).first()
    return {
        "id": alert.id,
        "field_id": alert.field_id,
        "field_name": f.name if f else alert.field_id.capitalize(),
        "alert_type": alert.alert_type,
        "severity": alert.severity,
        "title": alert.title,
        "message": alert.message,
        "suggested_action": alert.suggested_action,
        "status": alert.status,
        "created_at": alert.created_at
    }


@router.get("/stats")
def get_alert_stats(db: Session = Depends(get_db)):
    """Summary counts of alerts by severity and unread status."""
    total = db.query(Alert).count()
    unread = db.query(Alert).filter(Alert.status == "unread").count()
    critical = db.query(Alert).filter(Alert.severity == "critical", Alert.status == "unread").count()
    warning = db.query(Alert).filter(Alert.severity == "warning", Alert.status == "unread").count()
    return {
        "total": total,
        "unread": unread,
        "critical_unread": critical,
        "warning_unread": warning
    }

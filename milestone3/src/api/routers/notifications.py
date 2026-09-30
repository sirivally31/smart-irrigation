from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.db.models import Farmer, PushSubscription, NotificationPreference
from src.api.schemas import PushSubscriptionRequest
from src.services.notification_service import (
    VAPID_PUBLIC_KEY, send_web_push, send_sms, send_email
)

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


@router.get("/vapid-public-key")
def get_vapid_key():
    """Return the VAPID public key for Web Push browser subscription."""
    return {"vapid_public_key": VAPID_PUBLIC_KEY or "BExamplePublicKey_ReplaceWithYourGeneratedVapidPublicKeyHere"}


@router.post("/push/subscribe")
def subscribe_push(
    data: PushSubscriptionRequest,
    db: Session = Depends(get_db)
):
    """Save browser Web Push subscription credentials."""
    endpoint = data.endpoint
    p256dh = data.keys.get("p256dh", "")
    auth = data.keys.get("auth", "")

    existing = db.query(PushSubscription).filter(PushSubscription.endpoint == endpoint).first()
    if existing:
        existing.p256dh = p256dh
        existing.auth = auth
    else:
        new_sub = PushSubscription(
            farmer_id=1,
            endpoint=endpoint,
            p256dh=p256dh,
            auth=auth
        )
        db.add(new_sub)

    db.commit()
    return {"status": "success", "message": "Push notification subscription registered."}


@router.post("/push/test")
def test_push_notification(db: Session = Depends(get_db)):
    """Trigger a test Web Push notification to registered subscriptions."""
    subs = db.query(PushSubscription).filter(PushSubscription.farmer_id == 1).all()
    payload = {
        "title": "Smart Irrigation Test",
        "body": "Web Push test alert: Sensor and alert monitoring is active.",
        "icon": "/icons/icon-192x192.png",
        "data": {"url": "/alerts"}
    }
    if not subs:
        # Return simulated success with instructions
        return {
            "status": "simulated_success",
            "message": "No active browser push subscriptions registered yet. Allow notifications in your browser, or enjoy simulated demo mode.",
            "sample_payload": payload
        }

    results = []
    for s in subs:
        sub_info = {
            "endpoint": s.endpoint,
            "keys": {"p256dh": s.p256dh, "auth": s.auth}
        }
        res = send_web_push(sub_info, payload)
        results.append(res)

    return {"status": "success", "results": results}


@router.post("/sms/test")
def test_sms_notification(db: Session = Depends(get_db)):
    """Trigger a test SMS notification using Twilio or interactive demo mode."""
    farmer = db.query(Farmer).first()
    phone = farmer.phone if farmer else "+91 9876543210"
    msg = "Smart Irrigation Alert: Low soil moisture (26.5%) in North Plot (Tomato). Suggested: Execute 15m drip cycle."
    result = send_sms(phone, msg)
    return result


@router.post("/email/test")
def test_email_notification(db: Session = Depends(get_db)):
    """Trigger a test Email notification using SendGrid or interactive demo mode."""
    farmer = db.query(Farmer).first()
    email = farmer.email if farmer else "farmer@smartirrigation.local"
    subject = "Smart Irrigation Notification: Automated Test Alert"
    html = f"""
    <div style="font-family: Arial, sans-serif; padding: 20px; border: 1px solid #1B4D3E; border-radius: 8px;">
        <h2 style="color: #1B4D3E;">Smart Irrigation Assistant Test Notification</h2>
        <p>Dear {farmer.name if farmer else 'Farmer'},</p>
        <p>This is a test notification confirming that your SendGrid email alert dispatch is operational.</p>
        <div style="background-color: #E8F5E9; padding: 12px; border-radius: 6px; margin: 15px 0;">
            <strong>System Status:</strong> All ML models, rule engines, and sensors are active.
        </div>
        <p style="color: #666; font-size: 12px;">Smart Irrigation Assistant — Milestone 3</p>
    </div>
    """
    result = send_email(email, subject, html)
    return result

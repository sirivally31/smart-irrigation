from datetime import datetime
import json
import os
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from src.db.models import Farmer, NotificationPreference, PushSubscription, Alert

VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY", "")
VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY", "")
VAPID_CLAIMS_SUB = os.getenv("VAPID_CLAIMS_SUB", "mailto:admin@smartirrigation.local")

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "")

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", "alerts@smartirrigation.local")


def is_quiet_hours(prefs: NotificationPreference) -> bool:
    """Check if current local time is within configured quiet hours."""
    if not prefs or not prefs.quiet_hours_start or not prefs.quiet_hours_end:
        return False
    try:
        now_time = datetime.now().time()
        start_parts = [int(p) for p in prefs.quiet_hours_start.split(":")]
        end_parts = [int(p) for p in prefs.quiet_hours_end.split(":")]
        start_time = datetime.now().replace(hour=start_parts[0], minute=start_parts[1]).time()
        end_time = datetime.now().replace(hour=end_parts[0], minute=end_parts[1]).time()

        if start_time < end_time:
            return start_time <= now_time <= end_time
        else:  # crosses midnight
            return now_time >= start_time or now_time <= end_time
    except Exception:
        return False


# --- WEB PUSH NOTIFICATION DISPATCHER ---
def send_web_push(subscription_info: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
    """Send push notification via pywebpush. Falls back to simulated log if keys are missing or invalid."""
    try:
        from pywebpush import webpush, WebPushException
        if VAPID_PRIVATE_KEY and not VAPID_PRIVATE_KEY.startswith("Example"):
            webpush(
                subscription_info=subscription_info,
                data=json.dumps(payload),
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims={"sub": VAPID_CLAIMS_SUB}
            )
            return {"status": "sent", "mode": "real"}
        else:
            print(f"[Web Push Simulation] Payload to {subscription_info.get('endpoint', '')[:40]}...: {payload}")
            return {"status": "simulated_success", "mode": "demo", "payload": payload}
    except Exception as e:
        print(f"[Web Push Error / Demo Mode] {e}")
        return {"status": "simulated_success", "mode": "demo", "error": str(e), "payload": payload}


# --- TWILIO SMS DISPATCHER ---
def send_sms(to_phone: str, message: str) -> Dict[str, Any]:
    """Send SMS notification using Twilio. Operates in Demo Mode if credentials not supplied."""
    if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_PHONE_NUMBER and not TWILIO_ACCOUNT_SID.startswith("your_"):
        try:
            from twilio.rest import Client
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            res = client.messages.create(
                body=message,
                from_=TWILIO_PHONE_NUMBER,
                to=to_phone
            )
            return {"status": "sent", "mode": "real", "sid": res.sid}
        except Exception as e:
            print(f"[Twilio Error -> Falling back to Demo Mode] {e}")
            return {"status": "simulated_success", "mode": "demo", "to": to_phone, "message": message, "error": str(e)}
    else:
        print(f"[Twilio SMS Simulation] To: {to_phone} | Message: {message}")
        return {
            "status": "simulated_success",
            "mode": "demo",
            "to": to_phone,
            "message": message,
            "info": "Twilio credentials not configured in .env. Operates in interactive demo mode."
        }


# --- SENDGRID EMAIL DISPATCHER ---
def send_email(to_email: str, subject: str, html_content: str) -> Dict[str, Any]:
    """Send Email notification using SendGrid. Operates in Demo Mode if credentials not supplied."""
    if SENDGRID_API_KEY and not SENDGRID_API_KEY.startswith("your_"):
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail
            message = Mail(
                from_email=SENDGRID_FROM_EMAIL,
                to_emails=to_email,
                subject=subject,
                html_content=html_content
            )
            sg = SendGridAPIClient(SENDGRID_API_KEY)
            response = sg.send(message)
            return {"status": "sent", "mode": "real", "status_code": response.status_code}
        except Exception as e:
            print(f"[SendGrid Error -> Falling back to Demo Mode] {e}")
            return {"status": "simulated_success", "mode": "demo", "to": to_email, "subject": subject, "error": str(e)}
    else:
        print(f"[SendGrid Email Simulation] To: {to_email} | Subject: {subject}")
        return {
            "status": "simulated_success",
            "mode": "demo",
            "to": to_email,
            "subject": subject,
            "info": "SendGrid credentials not configured in .env. Operates in interactive demo mode."
        }


# --- CENTRALIZED DISPATCH FOR ALERTS ---
def dispatch_alert_notifications(db: Session, alert: Alert) -> Dict[str, Any]:
    """Check farmer preferences and dispatch alert via Web Push, SMS, and Email."""
    farmer = db.query(Farmer).first()
    if not farmer:
        return {"error": "No farmer found"}

    prefs = db.query(NotificationPreference).filter(NotificationPreference.farmer_id == farmer.id).first()
    results = {}

    # Quiet hours check: Critical alerts still go through; warnings are skipped during quiet hours
    quiet = is_quiet_hours(prefs)
    if quiet and alert.severity != "critical":
        return {"status": "skipped", "reason": "quiet_hours_active"}

    # 1. Web Push
    if prefs and prefs.enable_push:
        subs = db.query(PushSubscription).filter(PushSubscription.farmer_id == farmer.id).all()
        push_results = []
        payload = {
            "title": f"Alert: {alert.title}",
            "body": alert.message,
            "icon": "/icons/icon-192x192.png",
            "badge": "/icons/icon-192x192.png",
            "data": {
                "alert_id": alert.id,
                "field_id": alert.field_id,
                "url": f"/alerts"
            }
        }
        for sub in subs:
            sub_info = {
                "endpoint": sub.endpoint,
                "keys": {
                    "p256dh": sub.p256dh,
                    "auth": sub.auth
                }
            }
            push_results.append(send_web_push(sub_info, payload))
        results["push"] = push_results

    # 2. SMS (Critical or Warning only)
    if prefs and prefs.enable_sms and alert.severity in ["critical", "warning"]:
        sms_body = f"Smart Irrigation Alert: {alert.title} - {alert.message}. Action: {alert.suggested_action or 'Check app'}"
        results["sms"] = send_sms(farmer.phone, sms_body)

    # 3. Email
    if prefs and prefs.enable_email:
        email_subject = f"[{alert.severity.upper()}] {alert.title} - Smart Irrigation"
        email_html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
            <h2 style="color: {'#d9534f' if alert.severity == 'critical' else '#f0ad4e'};">{alert.title}</h2>
            <p><strong>Field:</strong> {alert.field_id.capitalize()}</p>
            <p><strong>Severity:</strong> {alert.severity.capitalize()}</p>
            <p><strong>Message:</strong> {alert.message}</p>
            <div style="background-color: #f8f9fa; padding: 12px; border-left: 4px solid #28a745; margin: 15px 0;">
                <strong>Suggested Action:</strong> {alert.suggested_action or 'Please review your dashboard.'}
            </div>
            <p style="font-size: 12px; color: #777;">Sent automatically by Smart Irrigation Assistant at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
        </div>
        """
        results["email"] = send_email(farmer.email, email_subject, email_html)

    return results

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.db.models import Farmer, NotificationPreference
from src.api.schemas import (
    FarmerProfileResponse, FarmerProfileUpdate,
    NotificationPreferenceResponse, NotificationPreferenceUpdate
)

router = APIRouter(prefix="/api/farmer", tags=["Farmer Profile & Preferences"])


@router.get("/profile", response_model=FarmerProfileResponse)
def get_farmer_profile(db: Session = Depends(get_db)):
    """Fetch current farmer profile details."""
    farmer = db.query(Farmer).first()
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer profile not found.")
    return farmer


@router.put("/profile", response_model=FarmerProfileResponse)
def update_farmer_profile(
    data: FarmerProfileUpdate,
    db: Session = Depends(get_db)
):
    """Update farmer profile information and preferred language."""
    farmer = db.query(Farmer).first()
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer profile not found.")

    for field_name, value in data.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(farmer, field_name, value)

    db.commit()
    db.refresh(farmer)
    return farmer


@router.get("/preferences", response_model=NotificationPreferenceResponse)
def get_preferences(db: Session = Depends(get_db)):
    """Fetch notification preferences and alert thresholds."""
    farmer = db.query(Farmer).first()
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found.")

    prefs = db.query(NotificationPreference).filter(NotificationPreference.farmer_id == farmer.id).first()
    if not prefs:
        prefs = NotificationPreference(farmer_id=farmer.id)
        db.add(prefs)
        db.commit()
        db.refresh(prefs)
    return prefs


@router.put("/preferences", response_model=NotificationPreferenceResponse)
def update_preferences(
    data: NotificationPreferenceUpdate,
    db: Session = Depends(get_db)
):
    """Update notification channels, quiet hours, and alert thresholds."""
    farmer = db.query(Farmer).first()
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found.")

    prefs = db.query(NotificationPreference).filter(NotificationPreference.farmer_id == farmer.id).first()
    if not prefs:
        prefs = NotificationPreference(farmer_id=farmer.id)
        db.add(prefs)

    update_dict = data.model_dump(exclude_unset=True)
    for key, val in update_dict.items():
        setattr(prefs, key, val)

    db.commit()
    db.refresh(prefs)
    return prefs

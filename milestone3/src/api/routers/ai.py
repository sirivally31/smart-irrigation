from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.api.schemas import (
    AIExplainRequest, AIExplainResponse,
    AIVoiceQueryRequest, AIVoiceQueryResponse
)
from src.services.sarvam_service import explain_recommendation, process_voice_query

router = APIRouter(prefix="/api/ai", tags=["Sarvam AI & Voice"])


@router.post("/explain", response_model=AIExplainResponse)
def explain_field_ai(
    data: AIExplainRequest,
    db: Session = Depends(get_db)
):
    """
    Generate dynamic farmer-friendly multilingual explanation (EN, HI, KN)
    of technical ML irrigation predictions using Sarvam AI with domain fallback.
    """
    res = explain_recommendation(data.field_id, data.language, db)
    if "error" in res:
        raise HTTPException(status_code=404, detail=res["error"])
    return res


@router.post("/voice-query", response_model=AIVoiceQueryResponse)
def handle_voice_query(
    data: AIVoiceQueryRequest,
    db: Session = Depends(get_db)
):
    """
    Process farmer voice query in English, Hindi, or Kannada,
    contextualized with real field sensor telemetry and ML predictions.
    """
    if not data.query or not data.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    res = process_voice_query(data.query, data.language, db, data.field_id)
    return res

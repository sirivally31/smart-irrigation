import io
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.services.report_service import generate_irrigation_pdf, generate_csv

router = APIRouter(prefix="/api/reports", tags=["Reports"])


@router.get("/pdf")
def download_pdf_report(
    field_id: Optional[str] = None,
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """Generate and stream a professional PDF irrigation and field status report."""
    pdf_bytes = generate_irrigation_pdf(db, field_id, days)
    filename = f"irrigation_report_{field_id or 'all'}_{datetime.utcnow().strftime('%Y%m%d')}.pdf"

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )


@router.get("/csv")
def download_csv_report(
    type: str = Query("irrigation", pattern="^(irrigation|sensors|alerts)$"),
    field_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Export irrigation records, sensor readings, or alert logs as CSV."""
    csv_text = generate_csv(db, type, field_id)
    filename = f"{type}_data_{field_id or 'all'}_{datetime.utcnow().strftime('%Y%m%d')}.csv"

    return StreamingResponse(
        io.StringIO(csv_text),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )

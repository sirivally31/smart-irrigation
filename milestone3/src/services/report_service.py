import io
import csv
from datetime import datetime, date, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from src.db.models import Farmer, Field, SensorReading, IrrigationRecord, IrrigationSchedule, Alert

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def generate_irrigation_pdf(
    db: Session,
    field_id: Optional[str] = None,
    days: int = 7
) -> bytes:
    """Generate a clean, printable PDF report using ReportLab."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1B4D3E')
    )
    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#555555')
    )
    section_title = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#2D7A4D'),
        spaceBefore=10,
        spaceAfter=6
    )
    body_style = styles['Normal']

    story = []

    # 1. Header
    farmer = db.query(Farmer).first()
    farmer_name = farmer.name if farmer else "Ramesh Patel"
    farmer_loc = farmer.location if farmer else "Dharwad, Karnataka"

    story.append(Paragraph("Smart Irrigation Assistant — Field & Irrigation Report", title_style))
    story.append(Paragraph(f"Farmer: <b>{farmer_name}</b> | Location: {farmer_loc} | Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1B4D3E'), spaceAfter=15))

    # 2. Scope & KPI Metrics
    start_date = datetime.utcnow() - timedelta(days=days)
    records_query = db.query(IrrigationRecord).filter(IrrigationRecord.timestamp >= start_date)
    readings_query = db.query(SensorReading).filter(SensorReading.timestamp >= start_date)

    if field_id:
        records_query = records_query.filter(IrrigationRecord.field_id == field_id)
        readings_query = readings_query.filter(SensorReading.field_id == field_id)

    records = records_query.order_by(IrrigationRecord.timestamp.desc()).all()
    readings = readings_query.all()

    total_water = sum(r.water_quantity_liters for r in records)
    total_duration = sum(r.duration_minutes for r in records)
    avg_moisture = round(sum(rd.soil_moisture_pct for rd in readings) / len(readings), 1) if readings else 0.0
    avg_temp = round(sum(rd.temperature_c for rd in readings) / len(readings), 1) if readings else 0.0

    kpi_data = [
        ["Reporting Period", "Total Events", "Total Water Applied", "Total Duration", "Avg Soil Moisture"],
        [f"Last {days} Days", f"{len(records)} cycles", f"{round(total_water, 1)} Liters", f"{round(total_duration, 1)} min", f"{avg_moisture}%"]
    ]
    kpi_table = Table(kpi_data, colWidths=[110, 80, 120, 95, 110])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E8F5E9')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1B4D3E')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#C8E6C9')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 15))

    # 3. Irrigation History Table
    story.append(Paragraph("Completed Irrigation Events", section_title))
    if records:
        history_rows = [["Date / Time (UTC)", "Field ID", "Duration (min)", "Water Applied (L)", "Status", "Notes"]]
        for r in records[:15]:  # limit to top 15 rows for neat page fit
            history_rows.append([
                r.timestamp.strftime('%Y-%m-%d %H:%M'),
                r.field_id.capitalize(),
                f"{r.duration_minutes} min",
                f"{r.water_quantity_liters} L",
                r.status.capitalize(),
                (r.notes or "Scheduled cycle")[:25]
            ])
        hist_table = Table(history_rows, colWidths=[105, 75, 75, 95, 75, 115])
        hist_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F5F7F2')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E0E0E0')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(hist_table)
    else:
        story.append(Paragraph("<i>No irrigation events recorded in this period.</i>", body_style))

    story.append(Spacer(1, 15))

    # 4. Today's ML Recommendations & Schedules
    story.append(Paragraph("Today's ML Recommendations & Schedules", section_title))
    sched_query = db.query(IrrigationSchedule).filter(IrrigationSchedule.schedule_date == date.today())
    if field_id:
        sched_query = sched_query.filter(IrrigationSchedule.field_id == field_id)
    schedules = sched_query.all()

    if schedules:
        sched_rows = [["Field", "Target Time", "Rec. Water", "Duration", "Status", "Reason"]]
        for s in schedules:
            sched_rows.append([
                s.field_id.capitalize(),
                s.recommended_start.strftime('%H:%M'),
                f"{s.water_quantity_liters} L",
                f"{s.duration_minutes} min",
                s.status.capitalize(),
                s.reason[:40]
            ])
        sched_table = Table(sched_rows, colWidths=[70, 75, 75, 70, 75, 175])
        sched_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F5F7F2')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E0E0E0')),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(sched_table)
    else:
        story.append(Paragraph("<i>No schedules generated for today.</i>", body_style))

    story.append(Spacer(1, 15))

    # 5. Alert History Summary
    story.append(Paragraph("Active & Recent Alerts", section_title))
    alerts_query = db.query(Alert).filter(Alert.created_at >= start_date)
    if field_id:
        alerts_query = alerts_query.filter(Alert.field_id == field_id)
    alerts = alerts_query.order_by(Alert.created_at.desc()).limit(6).all()

    if alerts:
        alert_rows = [["Timestamp", "Field", "Severity", "Alert Title", "Suggested Action"]]
        for a in alerts:
            alert_rows.append([
                a.created_at.strftime('%m-%d %H:%M'),
                a.field_id.capitalize(),
                a.severity.upper(),
                a.title[:35],
                (a.suggested_action or "Review status")[:35]
            ])
        alert_table = Table(alert_rows, colWidths=[80, 65, 65, 160, 170])
        alert_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F5F7F2')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E0E0E0')),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(alert_table)
    else:
        story.append(Paragraph("<i>No alerts logged for this period.</i>", body_style))

    # Build PDF
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


def generate_csv(
    db: Session,
    report_type: str,
    field_id: Optional[str] = None
) -> str:
    """Generate CSV string for irrigation, sensor, or alert history."""
    output = io.StringIO()
    writer = csv.writer(output)

    if report_type == "irrigation":
        writer.writerow(["record_id", "field_id", "timestamp_utc", "duration_minutes", "water_quantity_liters", "status", "notes"])
        q = db.query(IrrigationRecord).order_by(IrrigationRecord.timestamp.desc())
        if field_id:
            q = q.filter(IrrigationRecord.field_id == field_id)
        for r in q.all():
            writer.writerow([r.id, r.field_id, r.timestamp.isoformat(), r.duration_minutes, r.water_quantity_liters, r.status, r.notes or ""])

    elif report_type == "sensors":
        writer.writerow(["reading_id", "field_id", "timestamp_utc", "soil_moisture_pct", "temperature_c", "humidity_pct", "rainfall_mm", "wind_speed_mps", "solar_radiation_wm2", "is_simulated"])
        q = db.query(SensorReading).order_by(SensorReading.timestamp.desc()).limit(500)
        if field_id:
            q = q.filter(SensorReading.field_id == field_id)
        for s in q.all():
            writer.writerow([s.id, s.field_id, s.timestamp.isoformat(), s.soil_moisture_pct, s.temperature_c, s.humidity_pct, s.rainfall_mm, s.wind_speed_mps, s.solar_radiation_wm2, s.is_simulated])

    elif report_type == "alerts":
        writer.writerow(["alert_id", "field_id", "created_at_utc", "alert_type", "severity", "title", "message", "suggested_action", "status"])
        q = db.query(Alert).order_by(Alert.created_at.desc())
        if field_id:
            q = q.filter(Alert.field_id == field_id)
        for a in q.all():
            writer.writerow([a.id, a.field_id, a.created_at.isoformat(), a.alert_type, a.severity, a.title, a.message, a.suggested_action or "", a.status])

    else:
        writer.writerow(["error"])
        writer.writerow(["Unknown report type"])

    return output.getvalue()

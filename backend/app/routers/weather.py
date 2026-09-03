from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.entities import Field, WeatherData
from app.schemas.weather import WeatherResponse
from app.services.weather import fetch_weather

router = APIRouter(prefix="/api/v1", tags=["weather"])


async def weather_for_field(field: Field, db: Session) -> WeatherResponse:
    if field.latitude is None or field.longitude is None:
        raise HTTPException(status_code=422, detail="Field has no weather coordinates")
    weather = await fetch_weather(field.latitude, field.longitude)
    db.add(WeatherData(field_id=field.id, recorded_at=weather.timestamp, temperature=weather.temperature, humidity=weather.humidity, rainfall=weather.rainfall, rain_probability=weather.rain_probability, forecast=weather.forecast, source="openweathermap"))
    db.commit()
    return weather


@router.get("/weather", response_model=WeatherResponse)
async def get_weather(latitude: float = Query(ge=-90, le=90), longitude: float = Query(ge=-180, le=180), db: Session = Depends(get_db)) -> WeatherResponse:
    return await fetch_weather(latitude, longitude)


@router.get("/fields/{field_id}/weather", response_model=WeatherResponse)
async def get_field_weather(field_id: int, db: Session = Depends(get_db)) -> WeatherResponse:
    field = db.get(Field, field_id)
    if field is None:
        raise HTTPException(status_code=404, detail="Field not found")
    return await weather_for_field(field, db)
from datetime import datetime, timezone

import httpx
from fastapi import HTTPException

from app.config import settings
from app.schemas.weather import WeatherResponse


async def fetch_weather(latitude: float, longitude: float) -> WeatherResponse:
    if not settings.weather_api_key:
        raise HTTPException(status_code=503, detail="Weather API key is not configured")
    params = {"lat": latitude, "lon": longitude, "appid": settings.weather_api_key, "units": "metric"}
    try:
        async with httpx.AsyncClient(timeout=settings.weather_timeout_seconds) as client:
            current_response, forecast_response = await client.get(f"{settings.weather_api_base_url}/weather", params=params), await client.get(f"{settings.weather_api_base_url}/forecast", params=params)
            current_response.raise_for_status()
            forecast_response.raise_for_status()
            current = current_response.json()
            forecast_payload = forecast_response.json()
    except (httpx.HTTPError, ValueError) as error:
        raise HTTPException(status_code=502, detail="Weather provider unavailable or returned invalid data") from error

    try:
        rain = current.get("rain", {}).get("1h", 0.0)
        entries = forecast_payload["list"]
        forecast = [{"timestamp": entry["dt_txt"], "temperature": entry["main"]["temp"], "rain_probability": entry.get("pop", 0) * 100} for entry in entries[:8]]
        return WeatherResponse(
            latitude=latitude,
            longitude=longitude,
            temperature=float(current["main"]["temp"]),
            humidity=float(current["main"]["humidity"]),
            rainfall=float(rain),
            rain_probability=float(forecast[0]["rain_probability"] if forecast else 0),
            forecast=forecast,
            timestamp=datetime.now(timezone.utc),
        )
    except (KeyError, TypeError, ValueError, IndexError) as error:
        raise HTTPException(status_code=502, detail="Weather provider response is missing expected data") from error
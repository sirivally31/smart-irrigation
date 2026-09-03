from datetime import datetime

from pydantic import BaseModel, Field


class WeatherResponse(BaseModel):
    latitude: float
    longitude: float
    temperature: float
    humidity: float = Field(ge=0, le=100)
    rainfall: float = Field(ge=0)
    rain_probability: float = Field(ge=0, le=100)
    forecast: list[dict]
    timestamp: datetime
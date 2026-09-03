from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.schemas.configuration import FieldCreate
from app.schemas.readings import SensorReadingCreate
from app.schemas.weather import WeatherResponse


def test_field_coordinates_are_validated() -> None:
    with pytest.raises(ValidationError):
        FieldCreate(name="Field", farmer_id=1, latitude=91, longitude=78)


def test_reading_normalizes_timestamp_to_utc() -> None:
    reading = SensorReadingCreate(sensor_id=1, field_id=1, soil_moisture=42.5, timestamp="2026-09-03T10:30:00+02:00")
    assert reading.timestamp == datetime(2026, 9, 3, 8, 30, tzinfo=timezone.utc)


def test_weather_requires_expected_ranges() -> None:
    with pytest.raises(ValidationError):
        WeatherResponse(latitude=17, longitude=78, temperature=30, humidity=101, rainfall=0, rain_probability=20, forecast=[], timestamp=datetime.now(timezone.utc))
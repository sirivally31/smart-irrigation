from datetime import datetime

import pytest
from pydantic import ValidationError

from app.schemas.readings import SensorReadingCreate


def test_reading_requires_timezone() -> None:
    with pytest.raises(ValidationError):
        SensorReadingCreate(sensor_id=1, field_id=1, soil_moisture=42.5, timestamp=datetime(2026, 9, 3, 10, 30))


def test_reading_rejects_out_of_range_moisture() -> None:
    with pytest.raises(ValidationError):
        SensorReadingCreate(sensor_id=1, field_id=1, soil_moisture=101, timestamp="2026-09-03T10:30:00Z")
import pytest
from pydantic import ValidationError

from app.sensors.speed import SpeedPayload


def test_valid_payload() -> None:
    p = SpeedPayload(speed_mps=12.5, speed_kmh=45.0)
    assert p.speed_mps == 12.5


def test_rejects_out_of_range() -> None:
    with pytest.raises(ValidationError):
        SpeedPayload(speed_mps=999, speed_kmh=3600)

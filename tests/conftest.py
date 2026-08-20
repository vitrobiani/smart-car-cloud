import pytest


@pytest.fixture
def sample_envelope() -> dict:
    return {
        "sensor_id": "vehicle.speed",
        "ts_ms": 1_700_000_000_000,
        "trip_id": "22222222-2222-2222-2222-222222222222",
        "driver_id": "11111111-1111-1111-1111-111111111111",
        "status": "OK",
        "available": True,
        "payload": {"speed_mps": 12.5, "speed_kmh": 45.0},
    }

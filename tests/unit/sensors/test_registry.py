from app.sensors import SENSOR_REGISTRY


def test_all_14_sensors_registered() -> None:
    assert len(SENSOR_REGISTRY) == 14


def test_sensor_ids_match_docs() -> None:
    expected = {
        "vehicle.speed",
        "vehicle.accelerometer",
        "vehicle.rotation",
        "vehicle.pedals",
        "vehicle.energy",
        "vehicle.gears",
        "env.lighting",
        "vehicle.lights",
        "env.surroundings",
        "vehicle.adas",
        "vehicle.tires",
        "vehicle.turn_signals",
        "vehicle.parking_brake",
        "vehicle.odometer",
    }
    assert set(SENSOR_REGISTRY.keys()) == expected

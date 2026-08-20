from app.sensors import (
    accelerometer,
    adas,
    energy,
    gears,
    lighting,
    odometer,
    parking_brake,
    pedals,
    rotation,
    speed,
    surroundings,
    tires,
    turn_signals,
    vehicle_lights,
)
from app.sensors.base import Sensor

_ALL = [
    speed,
    accelerometer,
    rotation,
    pedals,
    energy,
    gears,
    lighting,
    vehicle_lights,
    surroundings,
    adas,
    tires,
    turn_signals,
    parking_brake,
    odometer,
]

SENSOR_REGISTRY: dict[str, Sensor] = {m.SENSOR.sensor_id: m.SENSOR for m in _ALL}


def get_sensor(sensor_id: str) -> Sensor | None:
    return SENSOR_REGISTRY.get(sensor_id)

from enum import Enum

from pydantic import BaseModel

from app.core.envelope import SampleType
from app.sensors.base import Sensor


class Headlights(str, Enum):
    OFF = "OFF"
    ON = "ON"
    DAYTIME_RUNNING = "DAYTIME_RUNNING"
    AUTOMATIC = "AUTOMATIC"


class HighBeam(str, Enum):
    OFF = "OFF"
    ON = "ON"
    AUTOMATIC = "AUTOMATIC"


class FogLights(str, Enum):
    OFF = "OFF"
    ON = "ON"
    UNAVAILABLE = "UNAVAILABLE"


class HazardLights(str, Enum):
    OFF = "OFF"
    ON = "ON"


class CabinLights(str, Enum):
    OFF = "OFF"
    ON = "ON"
    AUTOMATIC = "AUTOMATIC"


class VehicleLightsPayload(BaseModel):
    headlights: Headlights
    high_beam: HighBeam
    fog_lights_front: FogLights
    fog_lights_rear: FogLights
    hazard_lights: HazardLights
    cabin_lights: CabinLights
    driver_intent_matches_actual: bool


SENSOR = Sensor(
    sensor_id="vehicle.lights",
    payload_model=VehicleLightsPayload,
    sample_type=SampleType.ON_CHANGE,
)

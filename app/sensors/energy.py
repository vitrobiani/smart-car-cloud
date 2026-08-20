from enum import Enum

from pydantic import BaseModel, Field

from app.core.envelope import SampleType
from app.sensors.base import Sensor


class Powertrain(str, Enum):
    ICE = "ICE"
    EV = "EV"
    HYBRID = "HYBRID"


class ChargeState(str, Enum):
    NOT_CHARGING = "NOT_CHARGING"
    CHARGING = "CHARGING"
    FULL = "FULL"
    FAULT = "FAULT"


class EnergyPayload(BaseModel):
    powertrain: Powertrain
    fuel_level_l: float | None = Field(default=None, ge=0)
    fuel_level_pct: float | None = Field(default=None, ge=0, le=100)
    fuel_low: bool = False
    battery_level_wh: float | None = Field(default=None, ge=0)
    battery_level_pct: float | None = Field(default=None, ge=0, le=100)
    charging: bool = False
    charge_state: ChargeState | None = None
    range_remaining_m: float = Field(..., ge=0, le=1_000_000)


SENSOR = Sensor(
    sensor_id="vehicle.energy",
    payload_model=EnergyPayload,
    sample_type=SampleType.ON_CHANGE,
)

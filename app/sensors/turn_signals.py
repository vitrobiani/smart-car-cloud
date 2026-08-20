from enum import Enum

from pydantic import BaseModel, Field

from app.core.envelope import SampleType
from app.sensors.base import Sensor


class SignalState(str, Enum):
    NONE = "NONE"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    EMERGENCY = "EMERGENCY"


class TurnSignalsPayload(BaseModel):
    state: SignalState
    driver_intent: SignalState
    blink_count: int = Field(..., ge=0)
    duration_ms: int = Field(..., ge=0)


SENSOR = Sensor(
    sensor_id="vehicle.turn_signals",
    payload_model=TurnSignalsPayload,
    sample_type=SampleType.ON_CHANGE,
)

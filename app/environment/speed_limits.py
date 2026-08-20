"""Speed-limit lookup interface. Real impl uses TSR data or a speed-limit API."""
from pydantic import BaseModel


class SpeedLimit(BaseModel):
    limit_kmh: int


async def lookup(lat: float, lon: float) -> SpeedLimit:
    raise NotImplementedError("speed-limit provider not integrated")

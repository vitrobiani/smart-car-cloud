"""Weather lookup interface. Real impl calls an external weather API."""
from pydantic import BaseModel


class Weather(BaseModel):
    condition: str  # CLEAR | RAIN | SNOW | FOG
    temperature_c: float
    visibility_m: float


async def fetch(lat: float, lon: float) -> Weather:
    raise NotImplementedError("weather provider not integrated")

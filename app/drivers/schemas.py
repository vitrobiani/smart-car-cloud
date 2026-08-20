from datetime import datetime
from typing import Any

from pydantic import BaseModel


class DriverCreate(BaseModel):
    name: str
    persona: str | None = None
    preferences: dict[str, Any] | None = None


class DriverRead(BaseModel):
    id: int
    name: str | None = None
    persona: str | None = None
    preferences: dict[str, Any] | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class PersonaUpdate(BaseModel):
    persona: str

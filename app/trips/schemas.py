from datetime import datetime
from typing import Any

from pydantic import BaseModel


class TripRead(BaseModel):
    id: int
    driver_id: int | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    summary: dict[str, Any] | None = None

    model_config = {"from_attributes": True}


class TripSummaryRead(BaseModel):
    """Response for GET /trips/{id}/summary.

    Currently pulled from the `trips.summary` JSON blob written by the
    end-of-trip aggregation. Schema of that blob is defined by whichever
    processor writes it (owned outside this package).
    """
    trip_id: int
    summary: dict[str, Any] | None = None

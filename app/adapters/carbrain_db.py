"""Adapter to the smart_car_project database.

The DB schema is owned by smart_car_project; we consume it, we do not extend it.
This module is the ONLY place our code reaches into that package. If we need a
column or table that isn't there, coordinate with its maintainer — don't add it
here.

The sibling package isn't installable yet, so we prepend it to sys.path on
import. Swap that for a proper `pip install -e ../smart_car_project` once
they publish a pyproject.
"""
from __future__ import annotations

import sys
from collections.abc import Iterator
from pathlib import Path

_SIBLING = Path(__file__).resolve().parents[2] / "smart_car_project"
if str(_SIBLING) not in sys.path:
    sys.path.insert(0, str(_SIBLING))

from database import SessionLocal, engine  # noqa: E402
from models import Driver, Telemetry, Trip  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

__all__ = ["Driver", "Trip", "Telemetry", "SessionLocal", "engine", "get_session"]


def get_session() -> Iterator[Session]:
    """FastAPI dependency. Sync — FastAPI runs sync deps in a threadpool."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

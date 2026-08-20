"""Geofence lookup interface.

Not integrated: real impl reads geofence definitions from external config
(DB, feature-flag service, or user profile). No definitions are shipped in
code — hardcoding them would be a mock.
"""
from dataclasses import dataclass


@dataclass
class Geofence:
    name: str
    lat: float
    lon: float
    radius_m: float


def contains(lat: float, lon: float) -> list[Geofence]:
    raise NotImplementedError(
        "geofence source not wired — pending decision on where definitions live"
    )

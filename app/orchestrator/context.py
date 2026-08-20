from dataclasses import dataclass, field
from typing import Any


@dataclass
class ContextSnapshot:
    """Four-dimensional snapshot passed to the orchestrator and LLM."""

    user: dict[str, Any] = field(default_factory=dict)
    vehicle: dict[str, Any] = field(default_factory=dict)
    environment: dict[str, Any] = field(default_factory=dict)
    interaction: dict[str, Any] = field(default_factory=dict)


async def build_snapshot(trip_id: str) -> ContextSnapshot:
    """Assemble the current context for a trip. Reads hot store; TODO Redis backing."""
    return ContextSnapshot()

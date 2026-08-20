from fastapi import APIRouter

from app.orchestrator.context import ContextSnapshot, build_snapshot

router = APIRouter(prefix="/orchestrator", tags=["orchestrator"])


@router.get("/context/{trip_id}", response_model=ContextSnapshot)
async def get_context(trip_id: str) -> ContextSnapshot:
    return await build_snapshot(trip_id)

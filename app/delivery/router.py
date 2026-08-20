import asyncio
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from app.delivery import approval
from app.delivery.channel import Notification, dashboard

router = APIRouter(prefix="/notifications", tags=["delivery"])


class NotificationRead(BaseModel):
    trip_id: str
    channel: str
    message: str
    priority: int


@router.get("/{trip_id}", response_model=list[NotificationRead])
async def poll(trip_id: str) -> list[NotificationRead]:
    items = dashboard.drain(trip_id)
    return [NotificationRead(**item.__dict__) for item in items]


@router.websocket("/{trip_id}/ws")
async def ws(websocket: WebSocket, trip_id: str) -> None:
    await websocket.accept()
    try:
        while True:
            items = dashboard.drain(trip_id)
            for n in items:
                await websocket.send_json(NotificationRead(**n.__dict__).model_dump())
            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        return


class ApprovalRequestBody(BaseModel):
    trip_id: str
    reason: str


class ApprovalResolve(BaseModel):
    approve: bool


@router.post("/approvals")
def request_approval(body: ApprovalRequestBody) -> dict[str, str]:
    req = approval.request(body.trip_id, body.reason)
    return {"id": str(req.id), "status": req.status}


@router.post("/approvals/{req_id}")
def resolve_approval(req_id: UUID, body: ApprovalResolve) -> dict[str, str]:
    req = approval.resolve(req_id, body.approve)
    if req is None:
        return {"status": "not_found"}
    return {"id": str(req.id), "status": req.status}


async def emit(n: Notification) -> None:
    """Called by orchestrator to publish a notification."""
    await dashboard.send(n)

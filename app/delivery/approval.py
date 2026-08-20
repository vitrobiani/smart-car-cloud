from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class ApprovalRequest:
    id: UUID = field(default_factory=uuid4)
    trip_id: str = ""
    reason: str = ""
    status: str = "PENDING"  # PENDING | APPROVED | DENIED


_pending: dict[UUID, ApprovalRequest] = {}


def request(trip_id: str, reason: str) -> ApprovalRequest:
    req = ApprovalRequest(trip_id=trip_id, reason=reason)
    _pending[req.id] = req
    return req


def resolve(req_id: UUID, approve: bool) -> ApprovalRequest | None:
    req = _pending.get(req_id)
    if req is None:
        return None
    req.status = "APPROVED" if approve else "DENIED"
    return req

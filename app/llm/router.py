from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.llm.client import LlmUnavailable
from app.llm.uses import chatbot, summary

router = APIRouter(prefix="/llm", tags=["llm"])


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    reply: str


class SummaryResponse(BaseModel):
    summary: str


@router.post(
    "/chat",
    response_model=ChatResponse,
    responses={503: {"description": "LLM provider not integrated"}},
)
async def chat(payload: ChatRequest) -> ChatResponse:
    try:
        return ChatResponse(reply=await chatbot.reply(payload.question))
    except LlmUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc))


@router.post(
    "/trips/{trip_id}/summary",
    response_model=SummaryResponse,
    responses={503: {"description": "LLM provider not integrated"}},
)
async def trip_summary(trip_id: int) -> SummaryResponse:
    # Real impl pulls trip events from carbrain and passes descriptions here.
    try:
        text = await summary.summarize(f"trip {trip_id}")
        return SummaryResponse(summary=text)
    except LlmUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc))

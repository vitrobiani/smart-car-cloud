"""LLM client — talks to a local llama-server over its OpenAI-compatible API.

Bring the server up via `./run-local-llm.sh` (see repo root). Configure the
endpoint with LLM_BASE_URL / LLM_MODEL in .env if you need to point elsewhere.
"""
from typing import Any

import httpx

from app.config import settings


class LlmUnavailable(Exception):
    """Raised when the provider can't serve the request. Triggers degraded mode."""


class LlmClient:
    def __init__(self) -> None:
        self._client = httpx.AsyncClient(
            base_url=settings.llm_base_url,
            timeout=settings.llm_timeout_s,
        )

    async def complete(self, prompt: str, **kwargs: Any) -> str:
        payload = {
            "model": settings.llm_model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            **kwargs,
        }
        try:
            resp = await self._client.post("/chat/completions", json=payload)
            resp.raise_for_status()
        except (httpx.HTTPError, httpx.TimeoutException) as exc:
            raise LlmUnavailable(f"llm request failed: {exc}") from exc

        data = resp.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LlmUnavailable(f"unexpected llm response shape: {data!r}") from exc

    async def aclose(self) -> None:
        await self._client.aclose()


client = LlmClient()

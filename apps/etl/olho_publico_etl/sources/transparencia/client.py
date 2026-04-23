"""Portal da Transparência (CGU) — cliente HTTP.

- Header de auth: chave-api-dados
- Rate limit local: 90 req/min (respeita CGU)
- Retry exponencial em 429/5xx via tenacity
"""

from __future__ import annotations

import asyncio
from typing import Any

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .rate_limit import TokenBucket

BASE_URL = "https://api.portaldatransparencia.gov.br"
# Limite oficial CGU: 400 req/min em horário comercial, 700 entre 00h-06h.
# Usamos 400 como padrão seguro 24/7. APIs restritas (auxílio, bolsa família por
# beneficiário) têm limite de 180 — se for usar alguma, override com env var
# TRANSPARENCIA_RATE_PER_MINUTE.
DEFAULT_RATE_PER_MINUTE = 400


class TransparenciaClient:
    """Cliente HTTP para api.portaldatransparencia.gov.br."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = BASE_URL,
        rate_per_minute: int = DEFAULT_RATE_PER_MINUTE,
        timeout_seconds: float = 30.0,
    ):
        if not api_key:
            raise ValueError("api_key obrigatória (variável TRANSPARENCIA_API_KEY)")
        self._bucket = TokenBucket(rate_per_minute=rate_per_minute)
        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers={"chave-api-dados": api_key, "Accept": "application/json"},
            timeout=timeout_seconds,
        )

    async def __aenter__(self) -> TransparenciaClient:
        return self

    async def __aexit__(self, *exc_info) -> None:
        await self._client.aclose()

    async def aclose(self) -> None:
        await self._client.aclose()

    @retry(
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
        wait=wait_exponential(multiplier=1, min=1, max=30),
        stop=stop_after_attempt(5),
        reraise=True,
    )
    async def _request(self, method: str, path: str, **kwargs) -> httpx.Response:
        # bloqueia até ter token (rate limit)
        await asyncio.get_running_loop().run_in_executor(None, self._bucket.acquire)
        resp = await self._client.request(method, path, **kwargs)
        if resp.status_code == 429 or 500 <= resp.status_code < 600:
            raise httpx.HTTPStatusError(
                f"status={resp.status_code}", request=resp.request, response=resp
            )
        resp.raise_for_status()
        return resp

    async def get(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        resp = await self._request("GET", path, params=params)
        return resp.json()

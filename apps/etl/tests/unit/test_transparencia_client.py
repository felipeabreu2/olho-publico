import json
from pathlib import Path

import httpx
import pytest
import respx

from olho_publico_etl.sources.transparencia.client import TransparenciaClient

FIXTURE = Path(__file__).parent.parent / "fixtures" / "transparencia_convenios.json"


@pytest.mark.asyncio
async def test_client_envia_chave_api_no_header():
    with respx.mock(base_url="https://api.portaldatransparencia.gov.br") as mock:
        mock.get("/api-de-dados/transferencias").mock(
            return_value=httpx.Response(200, json=[])
        )
        async with TransparenciaClient(api_key="minha-chave") as c:
            await c.get("/api-de-dados/transferencias")
        req = mock.calls.last.request
        assert req.headers["chave-api-dados"] == "minha-chave"


@pytest.mark.asyncio
async def test_client_desserializa_json():
    payload = json.loads(FIXTURE.read_text())
    with respx.mock(base_url="https://api.portaldatransparencia.gov.br") as mock:
        mock.get("/api-de-dados/transferencias").mock(
            return_value=httpx.Response(200, json=payload)
        )
        async with TransparenciaClient(api_key="k") as c:
            data = await c.get("/api-de-dados/transferencias")
        assert len(data) == 2
        assert data[0]["municipioConvenente"]["codigoIBGE"] == "3550308"


@pytest.mark.asyncio
async def test_client_retry_em_429():
    with respx.mock(base_url="https://api.portaldatransparencia.gov.br") as mock:
        route = mock.get("/api-de-dados/transferencias").mock(
            side_effect=[
                httpx.Response(429, headers={"Retry-After": "0"}),
                httpx.Response(200, json=[{"ok": True}]),
            ]
        )
        async with TransparenciaClient(api_key="k") as c:
            data = await c.get("/api-de-dados/transferencias")
        assert route.call_count == 2
        assert data == [{"ok": True}]


@pytest.mark.asyncio
async def test_client_propaga_erro_4xx_nao_transitorio():
    with respx.mock(base_url="https://api.portaldatransparencia.gov.br") as mock:
        mock.get("/api-de-dados/transferencias").mock(
            return_value=httpx.Response(401, json={"error": "unauthorized"})
        )
        async with TransparenciaClient(api_key="k") as c:
            with pytest.raises(httpx.HTTPStatusError):
                await c.get("/api-de-dados/transferencias")

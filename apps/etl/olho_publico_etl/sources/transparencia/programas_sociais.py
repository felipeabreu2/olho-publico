"""Programas sociais por município — bolsa família, auxílio brasil, seguro defeso.

Cada um é endpoint distinto da CGU mas formato de resposta similar.
Todos retornam agregado mensal por município (sem dados individuais).
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from decimal import Decimal
from typing import Any

from ._helpers import ano_mes_to_aaaamm
from ._social import ProgramaSocialMes
from .client import TransparenciaClient

ENDPOINTS = {
    "bolsa_familia": "/api-de-dados/bolsa-familia-por-municipio",
    "auxilio_brasil": "/api-de-dados/novo-bolsa-familia-por-municipio",
    "seguro_defeso": "/api-de-dados/seguro-defeso-por-municipio",
}
MAX_PAGE_SIZE = 15


def _parse_payload(
    payload: list[dict[str, Any]], programa: str, ano_mes: str
) -> Iterator[ProgramaSocialMes]:
    for item in payload:
        municipio = item.get("municipio") or item.get("municipioBeneficiario") or {}
        municipio_id = municipio.get("codigoIBGE") or municipio.get("codigoIbge")
        if not municipio_id:
            continue
        valor = Decimal(str(item.get("valor") or item.get("valorTotal") or "0"))
        if valor <= 0:
            continue
        qtd = item.get("quantidadeBeneficiados") or item.get("quantidadeFamiliasBeneficiadas")
        valor_medio_raw = item.get("valorMedio")
        valor_medio = Decimal(str(valor_medio_raw)) if valor_medio_raw else None
        yield ProgramaSocialMes(
            municipio_id=str(municipio_id),
            programa=programa,  # type: ignore[arg-type]
            ano_mes=ano_mes,
            qtd_beneficiarios=int(qtd) if qtd else None,
            valor_total=valor,
            valor_medio_beneficiario=valor_medio,
        )


async def fetch_programa_municipio(
    client: TransparenciaClient,
    *,
    programa: str,
    codigo_ibge: str,
    ano_mes: str,
) -> AsyncIterator[ProgramaSocialMes]:
    """Pagina endpoint do programa para um município/mês.

    `programa` deve ser uma das chaves de ENDPOINTS.
    """
    if programa not in ENDPOINTS:
        raise ValueError(f"programa desconhecido: {programa}")
    endpoint = ENDPOINTS[programa]
    pagina = 1
    mes_ano = ano_mes_to_aaaamm(ano_mes)
    while True:
        params = {
            "codigoIbge": codigo_ibge,
            "mesAno": mes_ano,
            "pagina": pagina,
        }
        data = await client.get(endpoint, params=params)
        if not isinstance(data, list) or not data:
            return
        for r in _parse_payload(data, programa, ano_mes):
            yield r
        if len(data) < MAX_PAGE_SIZE:
            return
        pagina += 1

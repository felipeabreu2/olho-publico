"""Pessoas Politicamente Expostas — /api-de-dados/pessoa-politicamente-exposta."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from typing import Any

from pydantic import BaseModel

from olho_publico_etl.utils import mask_cpf

from ._helpers import parse_data_flex
from .client import TransparenciaClient

ENDPOINT = "/api-de-dados/pessoa-politicamente-exposta"
MAX_PAGE_SIZE = 15


class PessoaPepRecord(BaseModel):
    cpf_mascarado: str
    nome: str
    cargo: str | None = None
    orgao: str | None = None
    data_inicio: str | None = None  # YYYY-MM-DD ISO
    data_fim: str | None = None


def parse_pep_payload(payload: list[dict[str, Any]]) -> Iterator[PessoaPepRecord]:
    for item in payload:
        cpf_raw = item.get("cpf") or (item.get("pessoa") or {}).get("cpf")
        cpf_mask = mask_cpf(cpf_raw)
        nome = item.get("nome") or (item.get("pessoa") or {}).get("nome")
        if not cpf_mask or not nome:
            continue
        di = item.get("dataInicioExercicio") or item.get("dataInicio")
        df = item.get("dataFimExercicio") or item.get("dataFim")
        orgao_raw = item.get("orgao")
        orgao = orgao_raw.get("nome") if isinstance(orgao_raw, dict) else orgao_raw
        yield PessoaPepRecord(
            cpf_mascarado=cpf_mask,
            nome=nome,
            cargo=item.get("descricaoFuncao") or item.get("cargo"),
            orgao=orgao,
            data_inicio=parse_data_flex(di).isoformat() if di else None,
            data_fim=parse_data_flex(df).isoformat() if df else None,
        )


async def fetch_pep(client: TransparenciaClient) -> AsyncIterator[PessoaPepRecord]:
    pagina = 1
    while True:
        params = {"pagina": pagina}
        data = await client.get(ENDPOINT, params=params)
        if not isinstance(data, list) or not data:
            return
        for r in parse_pep_payload(data):
            yield r
        if len(data) < MAX_PAGE_SIZE:
            return
        pagina += 1

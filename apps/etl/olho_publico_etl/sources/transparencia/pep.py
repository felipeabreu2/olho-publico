"""Pessoas Politicamente Expostas — /api-de-dados/peps.

Endpoint exige ao menos um filtro (nome ou cpf). Pra pegar todos os PEPs,
iteramos pelo alfabeto A-Z em `nome` (cobertura ~completa, alguns nomes
acentuados podem escapar — limitação da API).
"""

from __future__ import annotations

import string
from collections.abc import AsyncIterator, Iterator
from typing import Any

from pydantic import BaseModel

from olho_publico_etl.utils import mask_cpf

from ._helpers import parse_data_flex
from .client import TransparenciaClient

ENDPOINT = "/api-de-dados/peps"
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
        # API retorna em snake_case nesta endpoint (diferente das outras!)
        cpf_raw = item.get("cpf") or item.get("cpf_mascarado")
        cpf_mask = mask_cpf(cpf_raw) if cpf_raw and "*" not in cpf_raw else cpf_raw
        nome = (item.get("nome") or "").strip()
        if not cpf_mask or not nome:
            continue
        cargo = (
            item.get("descricao_funcao")
            or item.get("descricaoFuncao")
            or item.get("cargo")
        )
        orgao = (
            item.get("nome_orgao")
            or item.get("orgao", {}).get("nome")
            if isinstance(item.get("orgao"), dict)
            else item.get("nome_orgao") or item.get("orgao")
        )
        di = (
            item.get("dt_inicio_exercicio")
            or item.get("dataInicioExercicio")
            or item.get("dataInicio")
        )
        df = (
            item.get("dt_fim_exercicio")
            or item.get("dataFimExercicio")
            or item.get("dataFim")
        )
        yield PessoaPepRecord(
            cpf_mascarado=cpf_mask,
            nome=nome,
            cargo=(cargo or "").strip() or None,
            orgao=(orgao or "").strip() if orgao else None,
            data_inicio=parse_data_flex(di).isoformat() if di else None,
            data_fim=parse_data_flex(df).isoformat() if df else None,
        )


async def _fetch_letra(
    client: TransparenciaClient, letra: str
) -> AsyncIterator[PessoaPepRecord]:
    pagina = 1
    while True:
        params = {"nome": letra, "pagina": pagina}
        data = await client.get(ENDPOINT, params=params)
        if not isinstance(data, list) or not data:
            return
        for r in parse_pep_payload(data):
            yield r
        if len(data) < MAX_PAGE_SIZE:
            return
        pagina += 1


async def fetch_pep(client: TransparenciaClient) -> AsyncIterator[PessoaPepRecord]:
    """Itera A-Z em `nome` para coletar todos os PEPs."""
    for letra in string.ascii_uppercase:
        async for r in _fetch_letra(client, letra):
            yield r

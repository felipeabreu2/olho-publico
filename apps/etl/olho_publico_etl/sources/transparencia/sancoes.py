"""Sanções administrativas — CEIS, CNEP, CEPIM, Acordos de Leniência.

CEIS: Cadastro Empresas Inidôneas e Suspensas
CNEP: Cadastro Nacional Empresas Punidas (Lei Anticorrupção)
CEPIM: Cadastro Empresas Impedidas (não podem receber repasse federal)
Leniência: Acordos de delação premiada empresarial
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from typing import Any

from olho_publico_etl.models import Sancao

from ._helpers import clean_cnpj, parse_data_flex
from .client import TransparenciaClient

ENDPOINT_CEIS = "/api-de-dados/ceis"
ENDPOINT_CNEP = "/api-de-dados/cnep"
ENDPOINT_CEPIM = "/api-de-dados/cepim"
ENDPOINT_LENIENCIA = "/api-de-dados/acordos-leniencia"
MAX_PAGE_SIZE = 15


def parse_sancoes_payload(payload: list[dict[str, Any]], origem: str) -> Iterator[Sancao]:
    """origem: 'CEIS' ou 'CNEP'."""
    for item in payload:
        empresa = item.get("pessoa") or item.get("sancionado") or {}
        cnpj = clean_cnpj(empresa.get("cnpjFormatado") or empresa.get("cpfCnpj"))
        if not cnpj:
            continue

        tipo = (item.get("tipoSancao") or {}).get("descricaoResumida") or origem
        orgao = (item.get("orgaoSancionador") or {}).get("nome") or "Órgão sancionador"
        motivo = item.get("fundamentacaoLegal") or item.get("descricaoFundamentacao")

        yield Sancao(
            cnpj=cnpj,
            tipo_sancao=f"{origem}: {tipo}"[:50],
            orgao_sancionador=orgao,
            data_inicio=parse_data_flex(item.get("dataInicioSancao") or item.get("dataPublicacao")),
            data_fim=(
                parse_data_flex(item.get("dataFimSancao"))
                if item.get("dataFimSancao") else None
            ),
            motivo=motivo,
            fonte_url=item.get("linkSancao"),
        )


async def fetch_ceis(client: TransparenciaClient) -> AsyncIterator[Sancao]:
    """Pagina /ceis (lista TODAS as sanções vigentes — sync mensal)."""
    pagina = 1
    while True:
        params = {"pagina": pagina}
        data = await client.get(ENDPOINT_CEIS, params=params)
        if not isinstance(data, list) or not data:
            return
        for s in parse_sancoes_payload(data, "CEIS"):
            yield s
        if len(data) < MAX_PAGE_SIZE:
            return
        pagina += 1


async def fetch_cnep(client: TransparenciaClient) -> AsyncIterator[Sancao]:
    """Pagina /cnep (lista TODAS as sanções vigentes — sync mensal)."""
    pagina = 1
    while True:
        params = {"pagina": pagina}
        data = await client.get(ENDPOINT_CNEP, params=params)
        if not isinstance(data, list) or not data:
            return
        for s in parse_sancoes_payload(data, "CNEP"):
            yield s
        if len(data) < MAX_PAGE_SIZE:
            return
        pagina += 1


async def fetch_cepim(client: TransparenciaClient) -> AsyncIterator[Sancao]:
    """Empresas impedidas de receber repasse federal."""
    pagina = 1
    while True:
        params = {"pagina": pagina}
        data = await client.get(ENDPOINT_CEPIM, params=params)
        if not isinstance(data, list) or not data:
            return
        for s in parse_sancoes_payload(data, "CEPIM"):
            yield s
        if len(data) < MAX_PAGE_SIZE:
            return
        pagina += 1


async def fetch_leniencia(client: TransparenciaClient) -> AsyncIterator[Sancao]:
    """Acordos de Leniência (delação empresarial)."""
    pagina = 1
    while True:
        params = {"pagina": pagina}
        data = await client.get(ENDPOINT_LENIENCIA, params=params)
        if not isinstance(data, list) or not data:
            return
        for s in parse_sancoes_payload(data, "LENIENCIA"):
            yield s
        if len(data) < MAX_PAGE_SIZE:
            return
        pagina += 1

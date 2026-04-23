"""Transferências federais mensais — /api-de-dados/transferencias.

Repasses diretos a municípios: SUS, FUNDEB, Auxílio Brasil, etc.
EXIGE chave gerada via Gov.br Prata/Ouro.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from datetime import date
from decimal import Decimal
from typing import Any

from olho_publico_etl.models import Contrato

from .client import TransparenciaClient

ENDPOINT = "/api-de-dados/transferencias"
MAX_PAGE_SIZE = 500


def _clean_cnpj(cnpj_formatted: str | None) -> str | None:
    if not cnpj_formatted:
        return None
    digits = "".join(c for c in cnpj_formatted if c.isdigit())
    return digits if len(digits) == 14 else None


def _ano_mes_to_ymd(ano_mes: str) -> str:
    """'2026-04' → '202604' (formato AAAAMM exigido pela API)."""
    return ano_mes.replace("-", "")


def _parse_mes_ano(s: str | None) -> date:
    """'2026-04' ou '04/2026' → date(2026, 4, 1)."""
    if not s:
        return date.today()
    if "-" in s:
        y, m = s.split("-")
        return date(int(y), int(m), 1)
    if "/" in s:
        m, y = s.split("/")
        return date(int(y), int(m), 1)
    return date.today()


def parse_transferencias_payload(payload: list[dict[str, Any]]) -> Iterator[Contrato]:
    """Converte resposta de /transferencias em Contrato."""
    for item in payload:
        favorecido = item.get("favorecido") or {}
        cnpj = _clean_cnpj(
            favorecido.get("codigoFormatado") or favorecido.get("cpfCnpj")
        )
        if not cnpj:
            continue

        municipio = item.get("municipio") or {}
        municipio_id = municipio.get("codigoIBGE") or None
        if not municipio_id:
            continue

        programa = (item.get("programa") or {}).get("descricao", "")
        acao = (item.get("acaoOrcamentaria") or {}).get("descricao", "")
        linguagem = item.get("linguagemCidada") or ""
        objeto_base = (f"{programa} — {acao}".strip(" —") or linguagem or "Transferência federal")
        objeto = f"[TRANSFERÊNCIA] {objeto_base}"

        valor_str = str(item.get("valor") or "0")
        valor = Decimal(valor_str)
        if valor <= 0:
            continue

        yield Contrato(
            municipio_aplicacao_id=municipio_id,
            cnpj_fornecedor=cnpj,
            orgao_contratante="Governo Federal",
            objeto=objeto,
            valor=valor,
            data_assinatura=_parse_mes_ano(item.get("mesAno")),
            modalidade_licitacao=None,
            fonte="portal_transparencia",
            dados_originais_url=None,
        )


async def fetch_transferencias_municipio(
    client: TransparenciaClient, *, codigo_ibge: str, ano_mes: str,
) -> AsyncIterator[Contrato]:
    pagina = 1
    mes_ano = _ano_mes_to_ymd(ano_mes)
    while True:
        params = {
            "codigoIbge": codigo_ibge,
            "mesAnoInicio": mes_ano,
            "mesAnoFim": mes_ano,
            "pagina": pagina,
        }
        data = await client.get(ENDPOINT, params=params)
        if not isinstance(data, list) or not data:
            return
        for c in parse_transferencias_payload(data):
            yield c
        if len(data) < MAX_PAGE_SIZE:
            return
        pagina += 1

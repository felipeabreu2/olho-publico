from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from datetime import date
from decimal import Decimal
from typing import Any

from olho_publico_etl.models import Contrato

from .client import TransparenciaClient

ENDPOINT = "/api-de-dados/transferencias"
MAX_PAGE_SIZE = 500


def _clean_cnpj(cnpj_formatted: str) -> str | None:
    digits = "".join(c for c in cnpj_formatted if c.isdigit())
    return digits if len(digits) == 14 else None


def _ano_mes_to_date(ano_mes: str) -> date:
    """'2025-01' → date(2025, 1, 1)."""
    ano, mes = ano_mes.split("-")
    return date(int(ano), int(mes), 1)


def parse_transferencias_payload(payload: list[dict[str, Any]]) -> Iterator[Contrato]:
    """Converte resposta de /transferencias em Contrato."""
    for item in payload:
        favorecido = item.get("favorecido", {}) or {}
        cnpj = _clean_cnpj(favorecido.get("codigoFormatado", ""))
        if not cnpj:
            continue
        municipio = item.get("municipio", {}) or {}
        municipio_id = municipio.get("codigoIBGE") or None

        programa = (item.get("programa") or {}).get("descricao", "")
        acao = (item.get("acaoOrcamentaria") or {}).get("descricao", "")
        linguagem = item.get("linguagemCidada") or ""
        objeto = f"{programa} — {acao}".strip(" —") or linguagem or "Transferência federal"

        yield Contrato(
            municipio_aplicacao_id=municipio_id,
            cnpj_fornecedor=cnpj,
            orgao_contratante="Governo Federal",
            objeto=objeto,
            valor=Decimal(str(item["valor"])),
            data_assinatura=_ano_mes_to_date(item["mesAno"]),
            modalidade_licitacao=None,
            fonte="portal_transparencia",
            dados_originais_url=None,
        )


async def fetch_transferencias_municipio(
    client: TransparenciaClient,
    *,
    codigo_ibge: str,
    ano_mes: str,
) -> AsyncIterator[Contrato]:
    """Pagina /transferencias para um município, mês a mês, até esgotar páginas."""
    pagina = 1
    while True:
        params = {
            "codigoIbge": codigo_ibge,
            "anoMesReferencia": ano_mes.replace("-", ""),  # API aceita YYYYMM
            "pagina": pagina,
        }
        data = await client.get(ENDPOINT, params=params)
        if not isinstance(data, list) or not data:
            return
        for contrato in parse_transferencias_payload(data):
            yield contrato
        if len(data) < MAX_PAGE_SIZE:
            return
        pagina += 1

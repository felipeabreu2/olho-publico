"""Transferências federais COVID-19 — /api-de-dados/coronavirus/transferencias."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from decimal import Decimal
from typing import Any

from olho_publico_etl.models import Contrato

from ._helpers import ano_mes_to_aaaamm, clean_cnpj, parse_data_flex
from .client import TransparenciaClient

ENDPOINT = "/api-de-dados/coronavirus/transferencias"
MAX_PAGE_SIZE = 15


def parse_coronavirus_payload(payload: list[dict[str, Any]]) -> Iterator[Contrato]:
    for item in payload:
        favorecido = item.get("favorecido") or item.get("convenente") or {}
        cnpj = clean_cnpj(favorecido.get("cnpjFormatado") or favorecido.get("cpfCnpj"))
        if not cnpj:
            continue

        municipio = item.get("municipio") or item.get("municipioConvenente") or {}
        municipio_id = municipio.get("codigoIBGE") or municipio.get("codigoIbge")
        if not municipio_id:
            continue

        descricao = item.get("descricao") or item.get("acao", {}).get("descricao") or ""
        objeto = (
            f"[COVID] {descricao}"[:500] if descricao
            else "[COVID] Transferência federal Covid-19"
        )

        valor_str = str(item.get("valor") or item.get("valorTransferido") or "0")
        valor = Decimal(valor_str)
        if valor <= 0:
            continue

        orgao = (item.get("orgao") or {}).get("nome") or "Governo Federal (COVID-19)"

        yield Contrato(
            municipio_aplicacao_id=str(municipio_id),
            cnpj_fornecedor=cnpj,
            orgao_contratante=orgao,
            objeto=objeto,
            valor=valor,
            data_assinatura=parse_data_flex(item.get("dataReferencia") or item.get("mesAno")),
            modalidade_licitacao="COVID_TRANSFERENCIA",
            fonte="portal_transparencia",
            dados_originais_url=None,
        )


async def fetch_coronavirus_municipio(
    client: TransparenciaClient, *, codigo_ibge: str, ano_mes: str,
) -> AsyncIterator[Contrato]:
    pagina = 1
    mes_ano = ano_mes_to_aaaamm(ano_mes)
    while True:
        params = {
            "codigoIbge": codigo_ibge,
            "mesAno": mes_ano,
            "pagina": pagina,
        }
        data = await client.get(ENDPOINT, params=params)
        if not isinstance(data, list) or not data:
            return
        for c in parse_coronavirus_payload(data):
            yield c
        if len(data) < MAX_PAGE_SIZE:
            return
        pagina += 1

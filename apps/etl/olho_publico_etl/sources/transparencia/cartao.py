"""Gastos com cartão de crédito corporativo federal — /api-de-dados/cartoes."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from decimal import Decimal
from typing import Any

from olho_publico_etl.models import Contrato

from ._helpers import ano_mes_to_aaaamm, clean_cnpj, parse_data_flex
from .client import TransparenciaClient

ENDPOINT = "/api-de-dados/cartoes"
MAX_PAGE_SIZE = 15


def parse_cartao_payload(payload: list[dict[str, Any]]) -> Iterator[Contrato]:
    for item in payload:
        # Estabelecimento que recebeu o pagamento (CNPJ)
        estab = item.get("estabelecimento") or {}
        cnpj = clean_cnpj(estab.get("cnpjFormatado") or estab.get("cpfCnpj"))
        if not cnpj:
            continue

        # Município de uso (estabelecimento) — pode vir em vários paths
        municipio_id = (
            (estab.get("municipio") or {}).get("codigoIBGE")
            or (item.get("municipio") or {}).get("codigoIBGE")
        )
        if not municipio_id:
            continue

        portador = (item.get("portador") or {}).get("nome") or "servidor"
        descricao = item.get("descricaoTransacao") or item.get("subElementoDespesa") or ""
        objeto_base = f"Cartão corporativo — {descricao}".strip(" —")[:500]
        if portador != "servidor":
            objeto_base += f" (portador: {portador})"
        objeto = f"[CARTÃO] {objeto_base}"

        valor_str = str(item.get("valorTransacao") or item.get("valor") or "0")
        valor = Decimal(valor_str)
        if valor <= 0:
            continue

        ug = item.get("unidadeGestora") or {}
        orgao = (ug.get("orgaoVinculado") or {}).get("nome") or "Governo Federal"

        yield Contrato(
            municipio_aplicacao_id=str(municipio_id),
            cnpj_fornecedor=cnpj,
            orgao_contratante=orgao,
            objeto=objeto,
            valor=valor,
            data_assinatura=parse_data_flex(item.get("dataTransacao") or item.get("data")),
            modalidade_licitacao="CARTAO_CORPORATIVO",
            fonte="portal_transparencia",
            dados_originais_url=None,
        )


async def fetch_cartao_municipio(
    client: TransparenciaClient, *, codigo_ibge: str, ano_mes: str,
) -> AsyncIterator[Contrato]:
    pagina = 1
    mes_ano = ano_mes_to_aaaamm(ano_mes)
    while True:
        params = {
            "codigoIbgeMunicipio": codigo_ibge,
            "mesExtratoInicio": mes_ano,
            "mesExtratoFim": mes_ano,
            "pagina": pagina,
        }
        data = await client.get(ENDPOINT, params=params)
        if not isinstance(data, list) or not data:
            return
        for c in parse_cartao_payload(data):
            yield c
        if len(data) < MAX_PAGE_SIZE:
            return
        pagina += 1

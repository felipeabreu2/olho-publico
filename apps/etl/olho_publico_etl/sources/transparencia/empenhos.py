"""Empenhos do Tesouro Nacional — /api-de-dados/despesas/empenhos."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from decimal import Decimal
from typing import Any

from olho_publico_etl.models import Contrato

from ._helpers import clean_cnpj, parse_data_flex
from .client import TransparenciaClient

ENDPOINT = "/api-de-dados/despesas/empenhos"
MAX_PAGE_SIZE = 15


def parse_empenhos_payload(payload: list[dict[str, Any]]) -> Iterator[Contrato]:
    for item in payload:
        favorecido = item.get("favorecido") or {}
        cnpj = clean_cnpj(favorecido.get("cnpjFormatado") or favorecido.get("cpfCnpj"))
        if not cnpj:
            continue

        municipio_id = (
            (item.get("municipio") or {}).get("codigoIBGE")
            or (item.get("favorecidoMunicipio") or {}).get("codigoIBGE")
            or (item.get("unidadeGestora") or {}).get("codigoIbgeMunicipio")
        )
        if not municipio_id:
            continue

        objeto_base = (
            item.get("observacao")
            or (item.get("acao") or {}).get("descricao")
            or "Empenho federal"
        ).strip()[:500]
        objeto = f"[EMPENHO] {objeto_base}"

        valor_str = str(item.get("valor") or item.get("valorEmpenhado") or "0")
        valor = Decimal(valor_str)
        if valor <= 0:
            continue

        orgao_obj = item.get("orgaoSuperior") or item.get("orgao") or {}
        orgao = orgao_obj.get("nome") or "Governo Federal"

        yield Contrato(
            municipio_aplicacao_id=str(municipio_id),
            cnpj_fornecedor=cnpj,
            orgao_contratante=orgao,
            objeto=objeto,
            valor=valor,
            data_assinatura=parse_data_flex(item.get("data") or item.get("dataEmissao")),
            modalidade_licitacao=None,
            fonte="portal_transparencia",
            dados_originais_url=None,
        )


async def fetch_empenhos_municipio(
    client: TransparenciaClient, *, codigo_ibge: str, ano_mes: str,
) -> AsyncIterator[Contrato]:
    pagina = 1
    ano, mes = ano_mes.split("-")
    data_inicial = f"01/{mes}/{ano}"
    data_final = f"28/{mes}/{ano}"
    while True:
        params = {
            "codigoIbgeFavorecido": codigo_ibge,
            "dataEmissaoInicio": data_inicial,
            "dataEmissaoFim": data_final,
            "pagina": pagina,
        }
        data = await client.get(ENDPOINT, params=params)
        if not isinstance(data, list) or not data:
            return
        for c in parse_empenhos_payload(data):
            yield c
        if len(data) < MAX_PAGE_SIZE:
            return
        pagina += 1

"""Recursos recebidos por favorecido — /api-de-dados/despesas/recursos-recebidos.

Mostra QUEM recebeu dinheiro federal num período. Bom complemento para
/transferencias quando essa exige permissão Ouro.
EXIGE Gov.br Ouro também — pode dar 403 com chave básica.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from decimal import Decimal
from typing import Any

from olho_publico_etl.models import Contrato

from ._helpers import ano_mes_to_aaaamm, clean_cnpj, parse_data_flex
from .client import TransparenciaClient

ENDPOINT = "/api-de-dados/despesas/recursos-recebidos"
MAX_PAGE_SIZE = 15


def parse_recursos_payload(payload: list[dict[str, Any]]) -> Iterator[Contrato]:
    for item in payload:
        favorecido = item.get("favorecido") or {}
        cnpj = clean_cnpj(favorecido.get("cnpjFormatado") or favorecido.get("cpfCnpj"))
        if not cnpj:
            continue

        municipio_id = (
            (favorecido.get("municipio") or {}).get("codigoIBGE")
            or (item.get("municipio") or {}).get("codigoIBGE")
        )
        if not municipio_id:
            continue

        descricao = (
            (item.get("acao") or {}).get("descricao")
            or item.get("descricao")
            or "Recurso federal recebido"
        )
        objeto = f"[RECURSO-RECEBIDO] {descricao}"[:500]

        valor_str = str(item.get("valor") or item.get("valorRecebido") or "0")
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
            data_assinatura=parse_data_flex(item.get("mesAno") or item.get("data")),
            modalidade_licitacao=None,
            fonte="portal_transparencia",
            dados_originais_url=None,
        )


async def fetch_recursos_municipio(
    client: TransparenciaClient, *, codigo_ibge: str, ano_mes: str,
) -> AsyncIterator[Contrato]:
    pagina = 1
    mes_ano = ano_mes_to_aaaamm(ano_mes)
    while True:
        params = {
            "codigoIbgeFavorecido": codigo_ibge,
            "mesAnoInicio": mes_ano,
            "mesAnoFim": mes_ano,
            "pagina": pagina,
        }
        data = await client.get(ENDPOINT, params=params)
        if not isinstance(data, list) or not data:
            return
        for c in parse_recursos_payload(data):
            yield c
        if len(data) < MAX_PAGE_SIZE:
            return
        pagina += 1

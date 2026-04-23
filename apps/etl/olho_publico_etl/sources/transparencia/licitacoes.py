"""Licitações federais — /api-de-dados/licitacoes."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from decimal import Decimal
from typing import Any

from olho_publico_etl.models import Contrato

from ._helpers import ano_mes_intervalo_ddmmyyyy, clean_cnpj, parse_data_flex
from .client import TransparenciaClient

ENDPOINT = "/api-de-dados/licitacoes"
MAX_PAGE_SIZE = 15


def parse_licitacoes_payload(payload: list[dict[str, Any]]) -> Iterator[Contrato]:
    for item in payload:
        # Vencedor da licitação (quando há um único vencedor identificado)
        vencedor = item.get("vencedor") or {}
        cnpj = clean_cnpj(vencedor.get("cnpjFormatado") or vencedor.get("cpfCnpj"))
        if not cnpj:
            continue

        municipio = item.get("municipio") or item.get("unidadeGestora", {}).get("municipio") or {}
        municipio_id = municipio.get("codigoIBGE") or municipio.get("codigoIbge")
        if not municipio_id:
            continue

        objeto_base = (item.get("objeto") or "Licitação federal").strip()[:500]
        modalidade_obj = item.get("modalidadeLicitacao") or {}
        modalidade = modalidade_obj.get("descricao") or item.get("modalidade")
        objeto = f"[LICITAÇÃO] {objeto_base}"

        valor_str = str(
            item.get("valorEstimado")
            or item.get("valorAdjudicado")
            or item.get("valor")
            or "0"
        )
        valor = Decimal(valor_str)
        if valor <= 0:
            continue

        orgao = (item.get("orgao") or {}).get("nome") or "Governo Federal"

        yield Contrato(
            municipio_aplicacao_id=str(municipio_id),
            cnpj_fornecedor=cnpj,
            orgao_contratante=orgao,
            objeto=objeto,
            valor=valor,
            data_assinatura=parse_data_flex(item.get("dataAbertura") or item.get("dataPublicacao")),
            modalidade_licitacao=modalidade,
            fonte="portal_transparencia",
            dados_originais_url=None,
        )


async def fetch_licitacoes_municipio(
    client: TransparenciaClient, *, codigo_ibge: str, ano_mes: str,
) -> AsyncIterator[Contrato]:
    pagina = 1
    data_inicial, data_final = ano_mes_intervalo_ddmmyyyy(ano_mes)
    while True:
        params = {
            "codigoMunicipio": codigo_ibge,
            "dataInicial": data_inicial,
            "dataFinal": data_final,
            "pagina": pagina,
        }
        data = await client.get(ENDPOINT, params=params)
        if not isinstance(data, list) or not data:
            return
        for c in parse_licitacoes_payload(data):
            yield c
        if len(data) < MAX_PAGE_SIZE:
            return
        pagina += 1

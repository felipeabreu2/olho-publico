"""Viagens de servidores federais — /api-de-dados/viagens.

Captura passagens + diárias quando o destino é um município brasileiro.
Sem CNPJ direto na maioria — registramos como contrato com CNPJ do órgão.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from decimal import Decimal
from typing import Any

from olho_publico_etl.models import Contrato

from ._helpers import clean_cnpj, parse_data_flex
from .client import TransparenciaClient

ENDPOINT = "/api-de-dados/viagens"
MAX_PAGE_SIZE = 15

# CNPJ genérico do União/Tesouro (placeholder para viagens sem fornecedor identificado).
# Necessário porque schema contratos exige CNPJ válido (14 dígitos).
CNPJ_PLACEHOLDER_GOV_FEDERAL = "00394460000141"  # CNPJ Tesouro Nacional


def parse_viagens_payload(payload: list[dict[str, Any]]) -> Iterator[Contrato]:
    for item in payload:
        # Município de destino — pode estar em vários paths
        destino = item.get("destinos", [{}])[0] if item.get("destinos") else item.get("destino", {})
        if not isinstance(destino, dict):
            destino = {}
        muni_obj = destino.get("municipio") or {}
        municipio_id = muni_obj.get("codigoIBGE") or destino.get("codigoIbge")
        if not municipio_id:
            continue

        valor_passagem = Decimal(str(item.get("valorPassagens") or "0"))
        valor_diarias = Decimal(str(item.get("valorDiarias") or "0"))
        valor_total = valor_passagem + valor_diarias
        if valor_total <= 0:
            continue

        proposto = (item.get("proposto") or {}).get("nome") or "servidor"
        motivo = item.get("motivo") or "Viagem oficial"
        objeto = f"[VIAGEM] {motivo} (proposto: {proposto})"[:500]

        orgao = (
            (item.get("orgaoSolicitante") or item.get("orgao") or {}).get("nome")
            or "Governo Federal"
        )
        # CNPJ do fornecedor: tentar empresa de viagem, senão Tesouro como placeholder
        fornecedor = item.get("fornecedorPassagens") or {}
        cnpj = clean_cnpj(fornecedor.get("cnpjFormatado")) or CNPJ_PLACEHOLDER_GOV_FEDERAL

        yield Contrato(
            municipio_aplicacao_id=str(municipio_id),
            cnpj_fornecedor=cnpj,
            orgao_contratante=orgao,
            objeto=objeto,
            valor=valor_total,
            data_assinatura=parse_data_flex(
                item.get("dataInicioAfastamento") or item.get("dataInicio")
            ),
            modalidade_licitacao="VIAGEM_OFICIAL",
            fonte="portal_transparencia",
            dados_originais_url=None,
        )


async def fetch_viagens_municipio(
    client: TransparenciaClient, *, codigo_ibge: str, ano_mes: str,
) -> AsyncIterator[Contrato]:
    pagina = 1
    ano, mes = ano_mes.split("-")
    data_inicial = f"01/{mes}/{ano}"
    data_final = f"28/{mes}/{ano}"
    while True:
        params = {
            "codigoIbgeMunicipioDestino": codigo_ibge,
            "dataIdaDe": data_inicial,
            "dataIdaAte": data_final,
            "pagina": pagina,
        }
        data = await client.get(ENDPOINT, params=params)
        if not isinstance(data, list) or not data:
            return
        for c in parse_viagens_payload(data):
            yield c
        if len(data) < MAX_PAGE_SIZE:
            return
        pagina += 1

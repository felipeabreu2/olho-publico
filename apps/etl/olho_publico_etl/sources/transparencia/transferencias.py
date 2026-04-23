"""Ingestão de dinheiro federal que vai para municípios via Portal da Transparência (CGU).

NOTA SOBRE ENDPOINT: idealmente usaríamos /api-de-dados/transferencias (repasses
mensais SUS, FUNDEB, etc.), mas esse endpoint exige chave gerada via Gov.br
Prata ou Ouro. Chaves geradas via CPF+2FA básico recebem 403 nesse endpoint.

Por enquanto, usamos /api-de-dados/convenios (parcerias federais) que cobre
boa parte do dinheiro federal a municípios e está acessível à chave básica.
Quando upgradar a chave, basta adicionar fetch para o endpoint /transferencias
em paralelo (ou criar transferencias_brutas.py).

Fonte gravada: 'portal_transparencia' (genérica) — em V2 separamos os tipos.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from datetime import date
from decimal import Decimal
from typing import Any

from olho_publico_etl.models import Contrato

from .client import TransparenciaClient

ENDPOINT = "/api-de-dados/convenios"
MAX_PAGE_SIZE = 15  # convenios retorna 15 por página (não 500)


def _clean_cnpj(cnpj_formatted: str) -> str | None:
    digits = "".join(c for c in cnpj_formatted if c.isdigit())
    return digits if len(digits) == 14 else None


def _ano_mes_to_intervalo(ano_mes: str) -> tuple[str, str]:
    """'2026-04' → ('01/04/2026', '30/04/2026'). Convenios exige DD/MM/YYYY."""
    ano, mes = ano_mes.split("-")
    return (f"01/{mes}/{ano}", f"28/{mes}/{ano}")  # 28 cobre fev sem cálculo de fim de mês


def _parse_data_publicacao(s: str | None) -> date:
    """Aceita 'YYYY-MM-DD' ou 'DD/MM/YYYY'."""
    if not s:
        return date.today()
    if "-" in s:
        return date.fromisoformat(s)
    d, m, y = s.split("/")
    return date(int(y), int(m), int(d))


def parse_transferencias_payload(payload: list[dict[str, Any]]) -> Iterator[Contrato]:
    """Converte resposta de /convenios em Contrato.

    Mantém o nome `parse_transferencias_payload` por compatibilidade com tests
    e jobs existentes — fonte interna passa a ser convenios federais.
    """
    for item in payload:
        convenente = item.get("convenente") or {}
        cnpj = _clean_cnpj(convenente.get("cnpjFormatado") or "")
        if not cnpj:
            continue

        municipio = item.get("municipioConvenente") or {}
        municipio_id = municipio.get("codigoIBGE") or None

        dim = item.get("dimConvenio") or {}
        objeto = (dim.get("objeto") or "Convênio federal").strip()

        orgao = item.get("orgao") or {}
        orgao_nome = orgao.get("nome") or "Governo Federal"

        # Preferimos valor (valor total firmado); valorLiberado é o pago até hoje.
        valor_str = str(item.get("valor") or item.get("valorLiberado") or "0")
        valor = Decimal(valor_str)
        if valor <= 0:
            continue

        yield Contrato(
            municipio_aplicacao_id=municipio_id,
            cnpj_fornecedor=cnpj,
            orgao_contratante=orgao_nome,
            objeto=objeto,
            valor=valor,
            data_assinatura=_parse_data_publicacao(item.get("dataPublicacao")),
            modalidade_licitacao=(item.get("tipoInstrumento") or {}).get("descricao"),
            fonte="portal_transparencia",
            dados_originais_url=None,
        )


async def fetch_transferencias_municipio(
    client: TransparenciaClient,
    *,
    codigo_ibge: str,
    ano_mes: str,
) -> AsyncIterator[Contrato]:
    """Pagina /convenios para um município, mês a mês, até esgotar páginas.

    A API CGU /convenios usa dataInicial + dataFinal em formato DD/MM/YYYY.
    """
    pagina = 1
    data_inicial, data_final = _ano_mes_to_intervalo(ano_mes)
    while True:
        params = {
            "codigoIBGE": codigo_ibge,
            "dataInicial": data_inicial,
            "dataFinal": data_final,
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

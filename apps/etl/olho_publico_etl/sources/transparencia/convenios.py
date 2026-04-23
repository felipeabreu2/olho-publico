"""Convenios federais — /api-de-dados/convenios.

Parcerias federais com municípios (obras, projetos, repasses condicionados).
Acessível com chave básica (não exige Gov.br Prata/Ouro).
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from datetime import date
from decimal import Decimal
from typing import Any

from olho_publico_etl.models import Contrato

from .client import TransparenciaClient

ENDPOINT = "/api-de-dados/convenios"
MAX_PAGE_SIZE = 15


def _clean_cnpj(cnpj_formatted: str) -> str | None:
    digits = "".join(c for c in cnpj_formatted if c.isdigit())
    return digits if len(digits) == 14 else None


def _ano_mes_to_intervalo(ano_mes: str) -> tuple[str, str]:
    ano, mes = ano_mes.split("-")
    return (f"01/{mes}/{ano}", f"28/{mes}/{ano}")


def _parse_data(s: str | None) -> date:
    if not s:
        return date.today()
    if "-" in s:
        return date.fromisoformat(s)
    d, m, y = s.split("/")
    return date(int(y), int(m), int(d))


def parse_convenios_payload(payload: list[dict[str, Any]]) -> Iterator[Contrato]:
    for item in payload:
        convenente = item.get("convenente") or {}
        cnpj = _clean_cnpj(convenente.get("cnpjFormatado") or "")
        if not cnpj:
            continue
        municipio = item.get("municipioConvenente") or {}
        municipio_id = municipio.get("codigoIBGE") or None

        dim = item.get("dimConvenio") or {}
        objeto_base = (dim.get("objeto") or "Convênio federal").strip()
        objeto = f"[CONVÊNIO] {objeto_base}"

        orgao = (item.get("orgao") or {}).get("nome") or "Governo Federal"
        valor_str = str(item.get("valor") or item.get("valorLiberado") or "0")
        valor = Decimal(valor_str)
        if valor <= 0:
            continue

        yield Contrato(
            municipio_aplicacao_id=municipio_id,
            cnpj_fornecedor=cnpj,
            orgao_contratante=orgao,
            objeto=objeto,
            valor=valor,
            data_assinatura=_parse_data(item.get("dataPublicacao")),
            modalidade_licitacao=(item.get("tipoInstrumento") or {}).get("descricao"),
            fonte="portal_transparencia",
            dados_originais_url=None,
        )


async def fetch_convenios_municipio(
    client: TransparenciaClient, *, codigo_ibge: str, ano_mes: str,
) -> AsyncIterator[Contrato]:
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
        for c in parse_convenios_payload(data):
            yield c
        if len(data) < MAX_PAGE_SIZE:
            return
        pagina += 1

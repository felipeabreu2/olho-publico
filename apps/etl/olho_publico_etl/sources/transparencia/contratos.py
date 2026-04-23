"""Contratos federais — /api-de-dados/contratos.

Contratos firmados pelo governo federal, com município de execução.
EXIGE chave Gov.br Prata/Ouro (e parâmetro codigoOrgao OU outro filtro).
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from datetime import date
from decimal import Decimal
from typing import Any

from olho_publico_etl.models import Contrato

from .client import TransparenciaClient

ENDPOINT = "/api-de-dados/contratos"
MAX_PAGE_SIZE = 15


def _clean_cnpj(s: str | None) -> str | None:
    if not s:
        return None
    digits = "".join(c for c in s if c.isdigit())
    return digits if len(digits) == 14 else None


def _parse_data(s: str | None) -> date:
    if not s:
        return date.today()
    if "-" in s:
        return date.fromisoformat(s)
    if "/" in s:
        d, m, y = s.split("/")
        return date(int(y), int(m), int(d))
    return date.today()


def parse_contratos_payload(payload: list[dict[str, Any]]) -> Iterator[Contrato]:
    """Converte resposta de /contratos em Contrato.

    Schema típico:
      - id, dataAssinatura, dataInicioVigencia, dataFimVigencia
      - valorInicialCompra, valorFinalCompra, valorEfetivamentePago
      - fornecedor.cpfFormatado / cnpjFormatado / nome
      - unidadeGestora, orgao
      - objeto (descrição)
      - municipio (?) ou inferido pela unidadeGestora.municipioCodigoIbge
    """
    for item in payload:
        fornecedor = item.get("fornecedor") or {}
        cnpj = _clean_cnpj(fornecedor.get("cnpjFormatado") or fornecedor.get("cpfCnpj"))
        if not cnpj:
            continue

        # Tenta extrair município de várias formas — o schema da API varia
        municipio_id = None
        for path in [
            ("municipio", "codigoIBGE"),
            ("municipio", "codigoIbge"),
            ("unidadeGestora", "municipio", "codigoIbge"),
            ("unidadeGestora", "codigoIbgeMunicipio"),
        ]:
            cur: Any = item
            for key in path:
                cur = (cur or {}).get(key) if isinstance(cur, dict) else None
                if cur is None:
                    break
            if cur:
                municipio_id = str(cur)
                break
        if not municipio_id:
            continue

        objeto_base = (item.get("objeto") or "Contrato federal").strip()[:500]
        objeto = f"[CONTRATO] {objeto_base}"

        orgao = (item.get("orgao") or {}).get("nome") or "Governo Federal"

        valor_str = str(
            item.get("valorInicialCompra")
            or item.get("valorFinalCompra")
            or item.get("valorEfetivamentePago")
            or "0"
        )
        valor = Decimal(valor_str)
        if valor <= 0:
            continue

        modalidade = (item.get("modalidadeCompra") or {}).get("descricao") or item.get("modalidade")

        yield Contrato(
            municipio_aplicacao_id=municipio_id,
            cnpj_fornecedor=cnpj,
            orgao_contratante=orgao,
            objeto=objeto,
            valor=valor,
            data_assinatura=_parse_data(
                item.get("dataAssinatura") or item.get("dataInicioVigencia")
            ),
            modalidade_licitacao=modalidade,
            fonte="portal_transparencia",
            dados_originais_url=None,
        )


async def fetch_contratos_municipio(
    client: TransparenciaClient, *, codigo_ibge: str, ano_mes: str,
) -> AsyncIterator[Contrato]:
    """Pagina /contratos filtrando por município de execução.

    A API exige dataInicial+dataFinal e aceita codigoMunicipio (opcional).
    """
    pagina = 1
    ano, mes = ano_mes.split("-")
    data_inicial = f"01/{mes}/{ano}"
    data_final = f"28/{mes}/{ano}"
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
        for c in parse_contratos_payload(data):
            yield c
        if len(data) < MAX_PAGE_SIZE:
            return
        pagina += 1

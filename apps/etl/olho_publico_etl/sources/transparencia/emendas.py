"""Emendas parlamentares — /api-de-dados/emendas.

"Deputado X destinou R$ Y para a cidade Z" — ouro para matérias.
EXIGE chave Gov.br Prata/Ouro.
"""

from __future__ import annotations

import contextlib
from collections.abc import AsyncIterator, Iterator
from datetime import date
from decimal import Decimal
from typing import Any

from olho_publico_etl.models import Contrato

from .client import TransparenciaClient

ENDPOINT = "/api-de-dados/emendas"
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


def parse_emendas_payload(payload: list[dict[str, Any]]) -> Iterator[Contrato]:
    """Converte resposta de /emendas em Contrato.

    Schema típico (varia conforme ano):
      - codigoEmenda, ano, autor (nome do parlamentar)
      - localidadeDoGasto.codigoIbge / municipioBeneficiario
      - valorEmpenhado, valorPago
      - funcao.descricao, subfuncao.descricao
      - favorecido.cpfCnpj
    """
    for item in payload:
        favorecidos = item.get("favorecidos")
        if isinstance(favorecidos, list) and favorecidos:
            favorecido = favorecidos[0] if isinstance(favorecidos[0], dict) else {}
        else:
            favorecido = item.get("favorecido") or {}
        if not isinstance(favorecido, dict):
            favorecido = {}
        cnpj = _clean_cnpj(favorecido.get("cpfCnpj") or favorecido.get("codigoFormatado"))
        if not cnpj:
            # Algumas emendas não têm favorecido CNPJ identificado — pula
            continue

        loc = item.get("localidadeDoGasto") or item.get("municipioBeneficiario") or {}
        municipio_id = loc.get("codigoIbge") or loc.get("codigoIBGE")
        if not municipio_id:
            continue

        autor = item.get("autor") or item.get("nomeAutor") or "Parlamentar não identificado"
        funcao = (item.get("funcao") or {}).get("descricao", "")
        subfuncao = (item.get("subfuncao") or {}).get("descricao", "")
        objeto_base = f"Emenda de {autor}"
        if funcao:
            objeto_base += f" — {funcao}"
        if subfuncao and subfuncao != funcao:
            objeto_base += f" / {subfuncao}"
        objeto = f"[EMENDA] {objeto_base}"

        valor_str = str(item.get("valorEmpenhado") or item.get("valorPago") or "0")
        valor = Decimal(valor_str)
        if valor <= 0:
            continue

        ano = item.get("ano")
        data_assinatura = _parse_data(item.get("dataReferencia") or item.get("dataInicial"))
        if ano and not item.get("dataReferencia"):
            with contextlib.suppress(TypeError, ValueError):
                data_assinatura = date(int(ano), 1, 1)

        yield Contrato(
            municipio_aplicacao_id=str(municipio_id),
            cnpj_fornecedor=cnpj,
            orgao_contratante=f"Emenda Parlamentar — {autor}",
            objeto=objeto,
            valor=valor,
            data_assinatura=data_assinatura,
            modalidade_licitacao="EMENDA",
            fonte="portal_transparencia",
            dados_originais_url=None,
        )


async def fetch_emendas_municipio(
    client: TransparenciaClient, *, codigo_ibge: str, ano_mes: str,
) -> AsyncIterator[Contrato]:
    """Pagina /emendas para um município. Emendas são tipicamente anuais."""
    pagina = 1
    ano = ano_mes.split("-")[0]
    while True:
        params = {
            "codigoIbgeBeneficiario": codigo_ibge,
            "ano": ano,
            "pagina": pagina,
        }
        data = await client.get(ENDPOINT, params=params)
        if not isinstance(data, list) or not data:
            return
        for c in parse_emendas_payload(data):
            yield c
        if len(data) < MAX_PAGE_SIZE:
            return
        pagina += 1

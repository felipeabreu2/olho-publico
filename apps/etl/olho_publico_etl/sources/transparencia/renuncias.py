"""Renúncias fiscais — /api-de-dados/renuncias-valor.

Empresas/setores que deixaram de pagar imposto (incentivos, isenções).
Dados anuais nacionais. Não tem CNPJ — armazenamos como agregado por ano.
Sem município direto, ficam fora de contratos. Vamos só logar e contar.
Em P3 podemos criar tabela renuncias_fiscais se quisermos persistir.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from decimal import Decimal
from typing import Any

from pydantic import BaseModel

from .client import TransparenciaClient

ENDPOINT = "/api-de-dados/renuncias-valor"
MAX_PAGE_SIZE = 15


class RenunciaFiscalAno(BaseModel):
    ano: int
    tipo_renuncia: str
    descricao_beneficio: str
    descricao_fundamento: str | None = None
    valor: Decimal


def parse_renuncias_payload(payload: list[dict[str, Any]]) -> Iterator[RenunciaFiscalAno]:
    for item in payload:
        try:
            ano = int(item.get("ano") or 0)
            valor = Decimal(str(item.get("valorRenunciado") or "0"))
        except (ValueError, TypeError):
            continue
        if not ano:
            continue
        yield RenunciaFiscalAno(
            ano=ano,
            tipo_renuncia=(item.get("tipoRenuncia") or "").strip()[:100],
            descricao_beneficio=(item.get("descricaoBeneficioFiscal") or "").strip()[:500],
            descricao_fundamento=(
                (item.get("descricaoFundamentoLegal") or "").strip()[:1000] or None
            ),
            valor=valor,
        )


async def fetch_renuncias(
    client: TransparenciaClient, *, ano: int,
) -> AsyncIterator[RenunciaFiscalAno]:
    pagina = 1
    while True:
        params = {"ano": ano, "pagina": pagina}
        data = await client.get(ENDPOINT, params=params)
        if not isinstance(data, list) or not data:
            return
        for r in parse_renuncias_payload(data):
            yield r
        if len(data) < MAX_PAGE_SIZE:
            return
        pagina += 1

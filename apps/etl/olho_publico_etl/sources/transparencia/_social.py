"""Helpers + modelo Pydantic para programas sociais (Bolsa Família, Aux Brasil, etc.)."""

from __future__ import annotations

from decimal import Decimal
from typing import Literal

from pydantic import BaseModel

ProgramaCodigo = Literal[
    "bolsa_familia",
    "novo_bolsa_familia",
    "auxilio_brasil",
    "seguro_defeso",
    "auxilio_emergencial",
    "bpc",
    "safra",
    "peti",
]


class ProgramaSocialMes(BaseModel):
    """Agregação mensal de programa social por município."""

    municipio_id: str
    programa: ProgramaCodigo
    ano_mes: str  # YYYY-MM
    qtd_beneficiarios: int | None = None
    valor_total: Decimal
    valor_medio_beneficiario: Decimal | None = None

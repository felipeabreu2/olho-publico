"""Receita Federal CNPJ base — placeholder downloader.

Real implementation in plan P3.
"""
from typing import Iterator

from olho_publico_etl.models import Empresa, Socio
from olho_publico_etl.sources.base import Source


class ReceitaCnpjSource(Source):
    name = "receita_cnpj"

    def fetch(self) -> Iterator[Empresa | Socio]:
        raise NotImplementedError("Implementado no plano P3 — exige download de 45 GB")

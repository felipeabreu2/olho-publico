"""Portal da Transparência (CGU) — placeholder client.

Real implementation in plan P2. This file pins the structure.
"""
from collections.abc import Iterator

from olho_publico_etl.models import Contrato
from olho_publico_etl.sources.base import Source


class TransparenciaSource(Source):
    name = "portal_transparencia"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def fetch(self) -> Iterator[Contrato]:
        raise NotImplementedError("Implementado no plano P2 — exige chave de API CGU")

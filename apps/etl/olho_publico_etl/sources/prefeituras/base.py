"""Base for ERP-based municipal scrapers.

Each subclass implements one ERP (E&L, IPM, Betha, Equiplano).
"""
from abc import abstractmethod
from typing import Iterator

from olho_publico_etl.models import Contrato
from olho_publico_etl.sources.base import Source


class PrefeituraErpSource(Source):
    erp_code: str

    def __init__(self, municipio_id: str, base_url: str):
        self.municipio_id = municipio_id
        self.base_url = base_url

    @abstractmethod
    def fetch(self) -> Iterator[Contrato]:
        """Implementação por ERP."""

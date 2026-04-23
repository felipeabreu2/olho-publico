from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import httpx

from olho_publico_etl.models import Municipio
from olho_publico_etl.utils import slugify

IBGE_MUNICIPIOS_URL = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"


def fetch_ibge_municipios(timeout_seconds: float = 30.0) -> list[dict[str, Any]]:
    """Baixa a lista completa de 5.570 municípios do IBGE."""
    with httpx.Client(timeout=timeout_seconds) as c:
        resp = c.get(IBGE_MUNICIPIOS_URL)
        resp.raise_for_status()
        return resp.json()


def parse_ibge_payload(payload: list[dict[str, Any]]) -> Iterator[Municipio]:
    """Converte resposta do IBGE em Municipio (Pydantic)."""
    for m in payload:
        id_ibge = str(m["id"]).zfill(7)
        nome = m["nome"]
        uf = m["microrregiao"]["mesorregiao"]["UF"]["sigla"]
        yield Municipio(
            id_ibge=id_ibge,
            nome=nome,
            slug=slugify(nome),
            uf=uf,
            cobertura_prefeitura="nenhuma",
        )

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


def _extract_uf(m: dict[str, Any]) -> str | None:
    """Extrai sigla da UF tolerando vários formatos do payload IBGE.

    O IBGE varia: alguns municípios têm `microrregiao`, outros
    `regiao-imediata` (formato novo), outros (DF) têm UF direto.
    """
    # Formato clássico: microrregiao → mesorregiao → UF
    microrregiao = m.get("microrregiao") or {}
    mesorregiao = microrregiao.get("mesorregiao") or {}
    uf = mesorregiao.get("UF") or {}
    sigla = uf.get("sigla")
    if sigla:
        return sigla

    # Formato novo (pós-reforma IBGE): regiao-imediata → regiao-intermediaria → UF
    ri = m.get("regiao-imediata") or {}
    ri_int = ri.get("regiao-intermediaria") or {}
    ri_uf = ri_int.get("UF") or {}
    sigla = ri_uf.get("sigla")
    if sigla:
        return sigla

    # Caso especial (DF e similares): UF direto no root
    root_uf = m.get("UF") or {}
    return root_uf.get("sigla")


def parse_ibge_payload(payload: list[dict[str, Any]]) -> Iterator[Municipio]:
    """Converte resposta do IBGE em Municipio (Pydantic).

    Pula registros sem UF identificável (não deve acontecer em produção,
    mas protege contra estruturas imprevistas).
    """
    for m in payload:
        uf = _extract_uf(m)
        if not uf:
            continue
        id_ibge = str(m["id"]).zfill(7)
        nome = m["nome"]
        yield Municipio(
            id_ibge=id_ibge,
            nome=nome,
            slug=slugify(nome),
            uf=uf,
            cobertura_prefeitura="nenhuma",
        )

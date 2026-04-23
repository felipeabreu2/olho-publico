from __future__ import annotations

from olho_publico_etl.db import make_pool
from olho_publico_etl.pipeline.gold import upsert_municipios
from olho_publico_etl.sources.ibge.municipios import (
    fetch_ibge_municipios,
    parse_ibge_payload,
)


def run(conninfo: str) -> int:
    """Baixa lista do IBGE e faz upsert em municipios. Retorna qtd inseridos/atualizados."""
    payload = fetch_ibge_municipios()
    municipios = list(parse_ibge_payload(payload))
    pool = make_pool(conninfo)
    try:
        with pool.connection() as conn:
            return upsert_municipios(conn, municipios)
    finally:
        pool.close()

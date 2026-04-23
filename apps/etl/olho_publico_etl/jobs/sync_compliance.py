"""Sync de dados de compliance: CEIS, CNEP, PEP.

Esses são datasets nacionais (não filtrados por município) — sync completo
mensal recomendado. Volume: ~milhares de registros cada.
"""
from __future__ import annotations

import asyncio
import traceback

from olho_publico_etl.config import Settings
from olho_publico_etl.db import make_pool
from olho_publico_etl.pipeline.gold import upsert_pep, upsert_sancoes
from olho_publico_etl.sources.transparencia.client import TransparenciaClient
from olho_publico_etl.sources.transparencia.pep import fetch_pep
from olho_publico_etl.sources.transparencia.sancoes import fetch_ceis, fetch_cnep


async def _collect_all(
    api_key: str, *, rate_per_minute: int, base_url: str
) -> tuple[list, list, list]:
    """Coleta CEIS + CNEP + PEP. Retorna (sancoes_ceis, sancoes_cnep, pep)."""
    ceis, cnep, pep = [], [], []
    async with TransparenciaClient(
        api_key=api_key, rate_per_minute=rate_per_minute, base_url=base_url
    ) as c:
        for nome, fetcher, target in [
            ("ceis", fetch_ceis, ceis),
            ("cnep", fetch_cnep, cnep),
            ("pep", fetch_pep, pep),
        ]:
            try:
                async for item in fetcher(c):
                    target.append(item)
                print(f"[sync-compliance] {nome}: {len(target)} registros", flush=True)
            except Exception as e:  # noqa: BLE001
                print(f"[sync-compliance] {nome} FALHOU: {e}", flush=True)
                traceback.print_exc()
    return ceis, cnep, pep


def sync_compliance(settings: Settings) -> dict[str, int]:
    """Sincroniza CEIS + CNEP + PEP (full sync mensal)."""
    ceis, cnep, pep = asyncio.run(
        _collect_all(
            settings.transparencia_api_key,
            rate_per_minute=settings.transparencia_rate_per_minute,
            base_url=settings.transparencia_base_url,
        )
    )

    pool = make_pool(settings.db_conninfo())
    try:
        with pool.connection() as conn:
            n_ceis = upsert_sancoes(conn, ceis)
            n_cnep = upsert_sancoes(conn, cnep)
            n_pep = upsert_pep(conn, pep)
    finally:
        pool.close()

    return {"ceis": n_ceis, "cnep": n_cnep, "pep": n_pep}

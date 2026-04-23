"""Sync de dados de compliance: CEIS, CNEP, CEPIM, Acordos Leniência, PEP.

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
from olho_publico_etl.sources.transparencia.sancoes import (
    fetch_ceis,
    fetch_cepim,
    fetch_cnep,
    fetch_leniencia,
)


async def _collect_all(
    api_key: str, *, rate_per_minute: int, base_url: str
) -> dict[str, list]:
    """Coleta CEIS + CNEP + CEPIM + Leniência + PEP."""
    results: dict[str, list] = {
        "ceis": [], "cnep": [], "cepim": [], "leniencia": [], "pep": [],
    }
    fetchers = [
        ("ceis", fetch_ceis),
        ("cnep", fetch_cnep),
        ("cepim", fetch_cepim),
        ("leniencia", fetch_leniencia),
        ("pep", fetch_pep),
    ]
    async with TransparenciaClient(
        api_key=api_key, rate_per_minute=rate_per_minute, base_url=base_url
    ) as c:
        for nome, fetcher in fetchers:
            try:
                async for item in fetcher(c):
                    results[nome].append(item)
                print(
                    f"[sync-compliance] {nome}: {len(results[nome])} registros",
                    flush=True,
                )
            except Exception as e:  # noqa: BLE001
                print(f"[sync-compliance] {nome} FALHOU: {e}", flush=True)
                traceback.print_exc()
    return results


def sync_compliance(settings: Settings) -> dict[str, int]:
    """Sincroniza CEIS + CNEP + CEPIM + Leniência + PEP."""
    results = asyncio.run(
        _collect_all(
            settings.transparencia_api_key,
            rate_per_minute=settings.transparencia_rate_per_minute,
            base_url=settings.transparencia_base_url,
        )
    )

    pool = make_pool(settings.db_conninfo())
    counts: dict[str, int] = {}
    try:
        with pool.connection() as conn:
            counts["ceis"] = upsert_sancoes(conn, results["ceis"])
            counts["cnep"] = upsert_sancoes(conn, results["cnep"])
            counts["cepim"] = upsert_sancoes(conn, results["cepim"])
            counts["leniencia"] = upsert_sancoes(conn, results["leniencia"])
            counts["pep"] = upsert_pep(conn, results["pep"])
    finally:
        pool.close()

    return counts

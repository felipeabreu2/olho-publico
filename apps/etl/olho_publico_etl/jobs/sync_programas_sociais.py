"""Sync de programas sociais por município/mês.

Bolsa Família, Auxílio Brasil (novo BF), Seguro Defeso.
Popula a tabela programas_sociais.
"""
from __future__ import annotations

import asyncio
import traceback

from olho_publico_etl.config import Settings
from olho_publico_etl.db import make_pool
from olho_publico_etl.pipeline.gold import upsert_programas_sociais
from olho_publico_etl.sources.transparencia._social import ProgramaSocialMes
from olho_publico_etl.sources.transparencia.client import TransparenciaClient
from olho_publico_etl.sources.transparencia.programas_sociais import (
    ENDPOINTS,
    fetch_programa_municipio,
)


async def _collect_all(
    api_key: str,
    codigo_ibge: str,
    ano_mes: str,
    *,
    rate_per_minute: int,
    base_url: str,
) -> list[ProgramaSocialMes]:
    """Coleta de TODOS os programas sociais para um município/mês."""
    out: list[ProgramaSocialMes] = []
    async with TransparenciaClient(
        api_key=api_key, rate_per_minute=rate_per_minute, base_url=base_url
    ) as c:
        for programa in ENDPOINTS:
            try:
                count = 0
                async for r in fetch_programa_municipio(
                    c, programa=programa, codigo_ibge=codigo_ibge, ano_mes=ano_mes
                ):
                    out.append(r)
                    count += 1
                print(
                    f"[sync-social] {programa} {codigo_ibge} {ano_mes}: {count} registros",
                    flush=True,
                )
            except Exception as e:  # noqa: BLE001
                print(
                    f"[sync-social] {programa} {codigo_ibge} {ano_mes} FALHOU: {e}",
                    flush=True,
                )
                traceback.print_exc()
    return out


def sync_programas_sociais_mes(
    settings: Settings, codigo_ibge: str, ano_mes: str
) -> int:
    registros = asyncio.run(
        _collect_all(
            settings.transparencia_api_key,
            codigo_ibge,
            ano_mes,
            rate_per_minute=settings.transparencia_rate_per_minute,
            base_url=settings.transparencia_base_url,
        )
    )
    if not registros:
        return 0

    pool = make_pool(settings.db_conninfo())
    try:
        with pool.connection() as conn:
            return upsert_programas_sociais(conn, registros)
    finally:
        pool.close()


def run_multiplas_cidades_sociais(
    settings: Settings, ibge_ids: list[str], ano_mes: str
) -> dict[str, int]:
    return {
        ibge: sync_programas_sociais_mes(settings, ibge, ano_mes) for ibge in ibge_ids
    }

"""Sync de programas sociais por município/mês.

Bolsa Família (legado, sem dados pós-2021/10), Novo Bolsa Família, Seguro Defeso.
Popula a tabela programas_sociais.

Nota: dados de programas sociais têm latência de ~3 meses para publicação.
Por isso buscamos dados do mês_atual - 3 (e depois - 4 e - 5 como fallback).
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

LOOKBACK_MESES = [3, 4, 5]  # tenta -3, -4, -5 meses se vazio


def _ano_mes_menos(ano_mes: str, n: int) -> str:
    y, m = ano_mes.split("-")
    total = int(y) * 12 + int(m) - 1 - n
    return f"{total // 12}-{(total % 12 + 1):02d}"


async def _collect_one_with_fallback(
    client: TransparenciaClient, *, programa: str, codigo_ibge: str, ano_mes_base: str
) -> tuple[list[ProgramaSocialMes], str]:
    """Tenta lookback de meses até achar dados. Retorna (lista, ano_mes_que_funcionou)."""
    for delta in LOOKBACK_MESES:
        am = _ano_mes_menos(ano_mes_base, delta)
        rows: list[ProgramaSocialMes] = []
        async for r in fetch_programa_municipio(
            client, programa=programa, codigo_ibge=codigo_ibge, ano_mes=am
        ):
            rows.append(r)
        if rows:
            return rows, am
    return [], _ano_mes_menos(ano_mes_base, LOOKBACK_MESES[-1])


async def _collect_all(
    api_key: str,
    codigo_ibge: str,
    ano_mes: str,
    *,
    rate_per_minute: int,
    base_url: str,
) -> list[ProgramaSocialMes]:
    out: list[ProgramaSocialMes] = []
    async with TransparenciaClient(
        api_key=api_key, rate_per_minute=rate_per_minute, base_url=base_url
    ) as c:
        for programa in ENDPOINTS:
            try:
                rows, am_real = await _collect_one_with_fallback(
                    c, programa=programa, codigo_ibge=codigo_ibge, ano_mes_base=ano_mes
                )
                out.extend(rows)
                print(
                    f"[sync-social] {programa} {codigo_ibge} (mês usado: {am_real}): "
                    f"{len(rows)} registros",
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

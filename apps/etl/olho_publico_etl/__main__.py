"""Entry point do container ETL.

Roda jobs agendados em loop simples (P2). Dagster entra depois.

Comportamento:
- Ao iniciar: sync IBGE (idempotente, rápido)
- A cada 6h: sync transferências para os IBGE_SYNC_LIST do mês atual
- Loop dorme 6h entre execuções
"""

from __future__ import annotations

import sys
import time
import traceback
from datetime import UTC, datetime

import psycopg

from olho_publico_etl import __version__
from olho_publico_etl.config import Settings, get_settings, require_settings
from olho_publico_etl.jobs.sync_compliance import sync_compliance
from olho_publico_etl.jobs.sync_ibge import run as run_sync_ibge
from olho_publico_etl.jobs.sync_programas_sociais import run_multiplas_cidades_sociais
from olho_publico_etl.jobs.sync_renuncias import sync_renuncias_ultimos_anos
from olho_publico_etl.jobs.sync_transferencias import run_multiplas_cidades

# Sync histórico de 12 meses × 10 cidades × 8 sources × paginação
# leva tempo. 24h entre ciclos é confortável e respeita rate limits.
JOB_INTERVAL_SECONDS = 24 * 3600  # 24h


def _ts() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _log(msg: str) -> None:
    print(f"[{_ts()}] [olho-publico-etl] {msg}", flush=True)


def _ano_mes_corrente() -> str:
    now = datetime.now(UTC)
    return f"{now.year}-{now.month:02d}"


def _ultimos_meses(n: int) -> list[str]:
    """Retorna lista de YYYY-MM, do mais antigo ao mais recente.

    Ex: _ultimos_meses(12) com hoje=2026-04 → ['2025-05', '2025-06', ..., '2026-04']
    """
    now = datetime.now(UTC)
    base_total = now.year * 12 + now.month - 1
    return [
        f"{(base_total - i) // 12}-{((base_total - i) % 12 + 1):02d}"
        for i in range(n - 1, -1, -1)
    ]


def _run_startup_jobs(settings: Settings) -> None:
    try:
        n = run_sync_ibge(settings.db_conninfo())
        _log(f"sync_ibge OK — {n} municipios upsertados")
    except Exception as e:  # noqa: BLE001
        _log(f"sync_ibge FALHOU: {e}")
        traceback.print_exc()


def _ibge_ids_todas_cidades(settings: Settings) -> list[str]:
    """Consulta tabela municipios e retorna todos os id_ibge cadastrados."""
    with psycopg.connect(settings.db_conninfo()) as conn, conn.cursor() as cur:
        cur.execute("SELECT id_ibge FROM municipios ORDER BY id_ibge")
        return [row[0] for row in cur.fetchall()]


def _resolve_ibge_ids(settings: Settings) -> list[str]:
    if settings.sync_todas_cidades:
        ids = _ibge_ids_todas_cidades(settings)
        _log(
            f"⚠️  SYNC_TODAS_CIDADES=true — sincronizando {len(ids)} cidades. "
            f"Ciclo levará MUITO mais tempo e consumirá rate limit pesadamente."
        )
        return ids
    return [x.strip() for x in settings.ibge_sync_list.split(",") if x.strip()]


def _run_periodic_jobs(settings: Settings) -> None:
    try:
        require_settings("transparencia_api_key")
    except RuntimeError as e:
        _log(f"jobs Transparencia pulados: {e}")
        return
    ibge_ids = _resolve_ibge_ids(settings)
    meses_lookback = settings.sync_meses_lookback

    _log(f"sync histórico — últimos {meses_lookback} meses para {len(ibge_ids)} cidade(s)")

    for ano_mes in _ultimos_meses(meses_lookback):
        # 1) Contratos federais (4 sources fail-soft)
        try:
            result = run_multiplas_cidades(settings, ibge_ids, ano_mes)
            total = sum(result.values())
            _log(f"sync contratos {ano_mes} — {total} novos registros (cidades: {len(result)})")
        except Exception as e:  # noqa: BLE001
            _log(f"sync contratos {ano_mes} FALHOU: {e}")
            traceback.print_exc()

        # 2) Programas sociais
        try:
            result = run_multiplas_cidades_sociais(settings, ibge_ids, ano_mes)
            total = sum(result.values())
            _log(f"sync sociais {ano_mes} — {total} registros")
        except Exception as e:  # noqa: BLE001
            _log(f"sync sociais {ano_mes} FALHOU: {e}")
            traceback.print_exc()

    # 3) Compliance (CEIS, CNEP, PEP — datasets nacionais, sync completo)
    try:
        result = sync_compliance(settings)
        _log(
            f"sync compliance — CEIS={result['ceis']} CNEP={result['cnep']} "
            f"CEPIM={result['cepim']} LENIENCIA={result['leniencia']} PEP={result['pep']}"
        )
    except Exception as e:  # noqa: BLE001
        _log(f"sync compliance FALHOU: {e}")
        traceback.print_exc()

    # 4) Renúncias fiscais (dados anuais nacionais — só log por enquanto)
    try:
        renuncias = sync_renuncias_ultimos_anos(settings)
        for ano, (qtd, total) in renuncias.items():
            _log(f"sync renuncias {ano} — {qtd} registros (R${total:,.2f})")
    except Exception as e:  # noqa: BLE001
        _log(f"sync renuncias FALHOU: {e}")
        traceback.print_exc()


def main() -> int:
    settings = get_settings()
    _log(f"v{__version__} iniciado")
    _log(f"database_url    : {'OK' if settings.database_url else 'AUSENTE'}")
    _log(f"transparencia   : {'OK' if settings.transparencia_api_key else 'AUSENTE'}")
    _log(f"r2_account_id   : {'OK' if settings.r2_account_id else 'AUSENTE'}")
    _log(f"ibge_sync_list  : {settings.ibge_sync_list}")

    # Jobs de startup (idempotentes)
    _run_startup_jobs(settings)

    try:
        while True:
            _run_periodic_jobs(settings)
            _log(f"próximo ciclo em {JOB_INTERVAL_SECONDS // 3600}h")
            time.sleep(JOB_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        _log("encerrando por SIGINT")
        return 0


if __name__ == "__main__":
    sys.exit(main())

"""Entry point do container ETL.

Roda jobs agendados em loop simples (P2). Dagster entra depois.

Comportamento:
- Ao iniciar: sync IBGE (idempotente, rápido)
- A cada 24h: sync histórico de N meses para todas as cidades configuradas
- Loop dorme 24h entre execuções
"""

from __future__ import annotations

import sys
import time
import traceback
from datetime import UTC, datetime

import psycopg

from olho_publico_etl import __version__, _log
from olho_publico_etl.config import Settings, get_settings, require_settings
from olho_publico_etl.jobs.sync_compliance import sync_compliance
from olho_publico_etl.jobs.sync_ibge import run as run_sync_ibge
from olho_publico_etl.jobs.sync_programas_sociais import run_multiplas_cidades_sociais
from olho_publico_etl.jobs.sync_renuncias import sync_renuncias_ultimos_anos
from olho_publico_etl.jobs.sync_transferencias import run_multiplas_cidades

JOB_INTERVAL_SECONDS = 24 * 3600


def _ultimos_meses(n: int) -> list[str]:
    now = datetime.now(UTC)
    base_total = now.year * 12 + now.month - 1
    return [
        f"{(base_total - i) // 12}-{((base_total - i) % 12 + 1):02d}"
        for i in range(n - 1, -1, -1)
    ]


def _fmt_erros(erros: dict[str, int], total_cidades: int) -> str:
    """Formata erros agregados: 'transferencias=403×5570 empenhos=403×5570'."""
    if not erros:
        return ""
    partes = [f"{src}×{n}/{total_cidades}" for src, n in sorted(erros.items())]
    return " falhas: " + " ".join(partes)


def _run_startup_jobs(settings: Settings) -> None:
    try:
        n = run_sync_ibge(settings.db_conninfo())
        _log.ok("ibge", f"{n} municipios upsertados")
    except Exception as e:  # noqa: BLE001
        _log.error("ibge", f"FALHOU: {e}")
        traceback.print_exc()


def _ibge_ids_todas_cidades(settings: Settings) -> list[str]:
    with psycopg.connect(settings.db_conninfo()) as conn, conn.cursor() as cur:
        cur.execute("SELECT id_ibge FROM municipios ORDER BY id_ibge")
        return [row[0] for row in cur.fetchall()]


def _resolve_ibge_ids(settings: Settings) -> list[str]:
    if settings.sync_todas_cidades:
        ids = _ibge_ids_todas_cidades(settings)
        _log.warn(
            "sync",
            f"SYNC_TODAS_CIDADES=true — {len(ids)} cidades. "
            f"Ciclo levará MUITO mais tempo e consumirá rate limit pesadamente.",
        )
        return ids
    ids = [x.strip() for x in settings.ibge_sync_list.split(",") if x.strip()]
    _log.info("sync", f"IBGE_SYNC_LIST — {len(ids)} cidade(s)")
    return ids


def _run_periodic_jobs(settings: Settings) -> None:
    try:
        require_settings("transparencia_api_key")
    except RuntimeError as e:
        _log.warn("sync", f"jobs Transparencia pulados: {e}")
        return

    ibge_ids = _resolve_ibge_ids(settings)
    meses_lookback = settings.sync_meses_lookback
    n_cidades = len(ibge_ids)

    _log.section(f"Ciclo: últimos {meses_lookback} meses × {n_cidades} cidades")

    for ano_mes in _ultimos_meses(meses_lookback):
        # 1) Contratos federais (multi-source fail-soft)
        try:
            por_cidade, erros = run_multiplas_cidades(settings, ibge_ids, ano_mes)
            total = sum(por_cidade.values())
            _log.ok(
                "contratos",
                f"{ano_mes} → {total} novos registros em {n_cidades} cidade(s)"
                + _fmt_erros(erros, n_cidades),
            )
        except Exception as e:  # noqa: BLE001
            _log.error("contratos", f"{ano_mes} FALHOU: {e}")
            traceback.print_exc()

        # 2) Programas sociais
        try:
            result = run_multiplas_cidades_sociais(settings, ibge_ids, ano_mes)
            total = sum(result.values())
            _log.ok("sociais", f"{ano_mes} → {total} registros")
        except Exception as e:  # noqa: BLE001
            _log.error("sociais", f"{ano_mes} FALHOU: {e}")
            traceback.print_exc()

    # 3) Compliance (CEIS, CNEP, PEP — datasets nacionais)
    try:
        r = sync_compliance(settings)
        _log.ok(
            "compliance",
            f"CEIS={r['ceis']} CNEP={r['cnep']} CEPIM={r['cepim']} "
            f"LENIENCIA={r['leniencia']} PEP={r['pep']}",
        )
    except Exception as e:  # noqa: BLE001
        _log.error("compliance", f"FALHOU: {e}")
        traceback.print_exc()

    # 4) Renúncias fiscais (anual nacional)
    try:
        renuncias = sync_renuncias_ultimos_anos(settings)
        for ano, (qtd, total) in renuncias.items():
            _log.ok("renuncias", f"{ano} → {qtd} registros (R$ {total:,.2f})")
    except Exception as e:  # noqa: BLE001
        _log.error("renuncias", f"FALHOU: {e}")
        traceback.print_exc()


def _check(label: str, ok: bool) -> str:
    return f"{label:<14} {'✓' if ok else '✗'}"


def main() -> int:
    settings = get_settings()
    _log.section(f"olho-publico-etl v{__version__}")
    _log.info("env", _check("database", bool(settings.database_url)))
    _log.info("env", _check("transparencia", bool(settings.transparencia_api_key)))
    _log.info("env", _check("r2", bool(settings.r2_account_id)))
    _log.info("env", f"meses_lookback {settings.sync_meses_lookback}")
    _log.info("env", f"sync_todas_cidades {settings.sync_todas_cidades}")

    _run_startup_jobs(settings)

    try:
        while True:
            _run_periodic_jobs(settings)
            _log.info("loop", f"próximo ciclo em {JOB_INTERVAL_SECONDS // 3600}h")
            time.sleep(JOB_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        _log.info("loop", "encerrando por SIGINT")
        return 0


if __name__ == "__main__":
    sys.exit(main())

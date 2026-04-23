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

from olho_publico_etl import __version__
from olho_publico_etl.config import Settings, get_settings, require_settings
from olho_publico_etl.jobs.sync_compliance import sync_compliance
from olho_publico_etl.jobs.sync_ibge import run as run_sync_ibge
from olho_publico_etl.jobs.sync_programas_sociais import run_multiplas_cidades_sociais
from olho_publico_etl.jobs.sync_transferencias import run_multiplas_cidades

JOB_INTERVAL_SECONDS = 6 * 3600  # 6h


def _ts() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _log(msg: str) -> None:
    print(f"[{_ts()}] [olho-publico-etl] {msg}", flush=True)


def _ano_mes_corrente() -> str:
    now = datetime.now(UTC)
    return f"{now.year}-{now.month:02d}"


def _run_startup_jobs(settings: Settings) -> None:
    try:
        n = run_sync_ibge(settings.db_conninfo())
        _log(f"sync_ibge OK — {n} municipios upsertados")
    except Exception as e:  # noqa: BLE001
        _log(f"sync_ibge FALHOU: {e}")
        traceback.print_exc()


def _run_periodic_jobs(settings: Settings) -> None:
    try:
        require_settings("transparencia_api_key")
    except RuntimeError as e:
        _log(f"jobs Transparencia pulados: {e}")
        return
    ibge_ids = [x.strip() for x in settings.ibge_sync_list.split(",") if x.strip()]
    ano_mes = _ano_mes_corrente()

    # 1) Contratos (8 sources: convenios, transferencias, emendas, contratos,
    #    licitacoes, empenhos, cartao, viagens)
    try:
        result = run_multiplas_cidades(settings, ibge_ids, ano_mes)
        for ibge, n in result.items():
            _log(f"sync contratos-like {ibge} {ano_mes} — {n} contratos totais")
    except Exception as e:  # noqa: BLE001
        _log(f"sync contratos-like FALHOU: {e}")
        traceback.print_exc()

    # 2) Programas sociais (bolsa familia, aux brasil, defeso)
    try:
        result = run_multiplas_cidades_sociais(settings, ibge_ids, ano_mes)
        for ibge, n in result.items():
            _log(f"sync programas sociais {ibge} {ano_mes} — {n} registros")
    except Exception as e:  # noqa: BLE001
        _log(f"sync programas sociais FALHOU: {e}")
        traceback.print_exc()

    # 3) Compliance (CEIS, CNEP, PEP — datasets nacionais, sync completo)
    try:
        result = sync_compliance(settings)
        _log(f"sync compliance — CEIS={result['ceis']} CNEP={result['cnep']} PEP={result['pep']}")
    except Exception as e:  # noqa: BLE001
        _log(f"sync compliance FALHOU: {e}")
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

"""Entry point do container ETL.

Em P1 (scaffolding) este módulo apenas:
1. Lê configuração e valida variáveis essenciais
2. Mantém o container vivo com heartbeat horário

Pipelines reais (Portal da Transparência, Receita CNPJ, etc.) entram em P2+
e vão substituir este loop por scheduler (Dagster ou cron interno).
"""

from __future__ import annotations

import sys
import time
from datetime import UTC, datetime

from olho_publico_etl import __version__
from olho_publico_etl.config import get_settings

HEARTBEAT_INTERVAL_SECONDS = 3600  # 1h


def _ts() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _log(msg: str) -> None:
    print(f"[{_ts()}] [olho-publico-etl] {msg}", flush=True)


def main() -> int:
    settings = get_settings()
    transparencia_status = (
        "OK" if settings.transparencia_api_key else "AUSENTE — pipelines federais paradas"
    )
    r2_status = "OK" if settings.r2_account_id else "AUSENTE — storage R2 desativado"

    _log(f"v{__version__} iniciado")
    _log(f"database_url    : {'OK' if settings.database_url else 'AUSENTE'}")
    _log(f"transparencia   : {transparencia_status}")
    _log(f"r2_account_id   : {r2_status}")
    _log(f"r2_bucket_raw   : {settings.r2_bucket_raw}")
    _log(f"r2_bucket_bronze: {settings.r2_bucket_bronze}")
    _log("Aguardando jobs agendados (implementação plena em P2+)...")

    try:
        while True:
            time.sleep(HEARTBEAT_INTERVAL_SECONDS)
            _log("heartbeat — sem jobs implementados em P1")
    except KeyboardInterrupt:
        _log("encerrando por SIGINT")
        return 0


if __name__ == "__main__":
    sys.exit(main())

"""Logger minimalista e legível para o ETL.

Formato:
    HH:MM:SS  LEVEL  [scope] mensagem

Mantém output limpo em stdout (sem libs externas, fácil para o Docker).
"""

from __future__ import annotations

import sys
from datetime import UTC, datetime

_USE_COLOR = sys.stdout.isatty()
_LEVELS = {
    "DEBUG": "\033[2;37m",   # cinza
    "INFO":  "\033[0;36m",   # ciano
    "OK":    "\033[0;32m",   # verde
    "WARN":  "\033[0;33m",   # amarelo
    "ERROR": "\033[0;31m",   # vermelho
}
_RESET = "\033[0m"


def _color(level: str) -> tuple[str, str]:
    if not _USE_COLOR:
        return "", ""
    return _LEVELS.get(level, ""), _RESET


def _ts() -> str:
    return datetime.now(UTC).strftime("%H:%M:%S")


def log(level: str, scope: str, msg: str) -> None:
    color, reset = _color(level)
    print(
        f"{_ts()}  {color}{level:<5}{reset}  [{scope}] {msg}",
        file=sys.stdout,
        flush=True,
    )


def info(scope: str, msg: str) -> None:
    log("INFO", scope, msg)


def ok(scope: str, msg: str) -> None:
    log("OK", scope, msg)


def warn(scope: str, msg: str) -> None:
    log("WARN", scope, msg)


def error(scope: str, msg: str) -> None:
    log("ERROR", scope, msg)


def section(title: str) -> None:
    """Separador visual entre fases do ciclo."""
    bar = "─" * 60
    print(f"\n{bar}\n  {title}\n{bar}", file=sys.stdout, flush=True)

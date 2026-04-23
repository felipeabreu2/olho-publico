from __future__ import annotations

from psycopg_pool import ConnectionPool


def make_pool(conninfo: str, *, min_size: int = 1, max_size: int = 5) -> ConnectionPool:
    """Cria pool de conexões Postgres reutilizável.

    min_size=1 evita lazy-connect na primeira query.
    max_size=5 é suficiente para ETL single-threaded (ingestão sequencial).
    """
    return ConnectionPool(
        conninfo=conninfo,
        min_size=min_size,
        max_size=max_size,
        open=True,
    )

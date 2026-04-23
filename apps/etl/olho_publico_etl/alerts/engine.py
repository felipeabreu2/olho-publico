"""Alert engine — runs all rules and persists alerts into Postgres."""
from collections.abc import Iterator

from olho_publico_etl.models import Alerta

from .rules import ALL_RULES


def run_all_rules(conn) -> Iterator[Alerta]:
    """Run every rule against the DB and yield each alert produced."""
    for rule in ALL_RULES:
        try:
            yield from rule.detectar(conn)
        except NotImplementedError:
            continue

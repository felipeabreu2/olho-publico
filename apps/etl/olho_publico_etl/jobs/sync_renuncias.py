"""Sync de renúncias fiscais — dados nacionais anuais.

Por enquanto só LOGA total — em P3 podemos criar tabela renuncias_fiscais.
"""
from __future__ import annotations

import asyncio
import traceback
from datetime import datetime
from decimal import Decimal

from olho_publico_etl.config import Settings
from olho_publico_etl.sources.transparencia.client import TransparenciaClient
from olho_publico_etl.sources.transparencia.renuncias import fetch_renuncias


async def _collect_anos(
    api_key: str, anos: list[int], *, rate_per_minute: int, base_url: str
) -> dict[int, tuple[int, Decimal]]:
    """Retorna {ano: (qtd_registros, soma_valor)}."""
    out: dict[int, tuple[int, Decimal]] = {}
    async with TransparenciaClient(
        api_key=api_key, rate_per_minute=rate_per_minute, base_url=base_url
    ) as c:
        for ano in anos:
            try:
                qtd = 0
                total = Decimal(0)
                async for r in fetch_renuncias(c, ano=ano):
                    qtd += 1
                    total += r.valor
                out[ano] = (qtd, total)
                print(
                    f"[sync-renuncias] {ano}: {qtd} registros, "
                    f"total R${total:,.2f}",
                    flush=True,
                )
            except Exception as e:  # noqa: BLE001
                print(f"[sync-renuncias] {ano} FALHOU: {e}", flush=True)
                traceback.print_exc()
    return out


def sync_renuncias_ultimos_anos(
    settings: Settings, n_anos: int = 5
) -> dict[int, tuple[int, Decimal]]:
    """Sincroniza renúncias dos últimos N anos. Em P3, persiste em tabela própria."""
    ano_atual = datetime.utcnow().year
    anos = list(range(ano_atual - n_anos, ano_atual))
    return asyncio.run(
        _collect_anos(
            settings.transparencia_api_key,
            anos,
            rate_per_minute=settings.transparencia_rate_per_minute,
            base_url=settings.transparencia_base_url,
        )
    )

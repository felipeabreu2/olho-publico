"""Helpers compartilhados pelos sources Transparência."""

from __future__ import annotations

from datetime import date


def clean_cnpj(s: str | None) -> str | None:
    if not s:
        return None
    digits = "".join(c for c in s if c.isdigit())
    return digits if len(digits) == 14 else None


def parse_data_flex(s: str | None) -> date:
    """Aceita YYYY-MM-DD, DD/MM/YYYY, ou retorna hoje se inválido."""
    if not s:
        return date.today()
    if isinstance(s, str):
        if "-" in s and len(s) >= 10:
            try:
                return date.fromisoformat(s[:10])
            except ValueError:
                pass
        if "/" in s:
            try:
                d, m, y = s.split("/")
                return date(int(y), int(m), int(d))
            except (ValueError, TypeError):
                pass
    return date.today()


def ano_mes_intervalo_ddmmyyyy(ano_mes: str) -> tuple[str, str]:
    """'2026-04' → ('01/04/2026', '28/04/2026'). 28 cobre fev sem cálculo."""
    ano, mes = ano_mes.split("-")
    return (f"01/{mes}/{ano}", f"28/{mes}/{ano}")


def ano_mes_to_aaaamm(ano_mes: str) -> str:
    """'2026-04' → '202604'."""
    return ano_mes.replace("-", "")

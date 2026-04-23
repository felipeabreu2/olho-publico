"""IBGE — municípios, população e IDH."""

from .municipios import fetch_ibge_municipios, parse_ibge_payload

__all__ = ["fetch_ibge_municipios", "parse_ibge_payload"]

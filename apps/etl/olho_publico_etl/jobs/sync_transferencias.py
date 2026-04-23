"""Sync de dinheiro federal por município — orquestra múltiplas fontes da CGU.

Cada source é fail-soft: se um endpoint específico falhar (403, schema mudou),
loga e segue com os outros. Garante cobertura parcial mesmo com problemas
em um endpoint específico.
"""
from __future__ import annotations

import asyncio
import traceback

from olho_publico_etl.config import Settings
from olho_publico_etl.db import make_pool
from olho_publico_etl.models import Contrato, Empresa
from olho_publico_etl.pipeline.bronze import (
    bronze_key_transferencias,
    contratos_to_parquet_bytes,
)
from olho_publico_etl.pipeline.gold import upsert_contratos, upsert_empresas
from olho_publico_etl.sources.transparencia.cartao import fetch_cartao_municipio
from olho_publico_etl.sources.transparencia.client import TransparenciaClient
from olho_publico_etl.sources.transparencia.contratos import fetch_contratos_municipio
from olho_publico_etl.sources.transparencia.convenios import fetch_convenios_municipio
from olho_publico_etl.sources.transparencia.emendas import fetch_emendas_municipio
from olho_publico_etl.sources.transparencia.empenhos import fetch_empenhos_municipio
from olho_publico_etl.sources.transparencia.licitacoes import fetch_licitacoes_municipio
from olho_publico_etl.sources.transparencia.transferencias import (
    fetch_transferencias_municipio,
)
from olho_publico_etl.sources.transparencia.viagens import fetch_viagens_municipio
from olho_publico_etl.storage.r2 import make_r2_client, upload_bytes

from .recompute_agregacoes import recompute_agregacoes_municipio

# Sources que populam `contratos`. Cada uma é fail-soft.
#
# DESATIVADAS (exigem codigoOrgao obrigatório — impraticável filtrar
# por município sem iterar todos os ~500 órgãos federais):
#   /contratos, /licitacoes, /viagens, /cartao (parcial)
#
# REQUEREM Gov.br Ouro: /transferencias, /despesas/empenhos, /cartoes
# (vão dar 403 com chave básica — tratado fail-soft pelo loop).
SOURCES = [
    ("convenios", fetch_convenios_municipio),  # ✓ funciona com básica
    ("transferencias", fetch_transferencias_municipio),  # requer Gov.br Ouro
    ("emendas", fetch_emendas_municipio),  # ✓ funciona
    ("empenhos", fetch_empenhos_municipio),  # requer Gov.br Ouro
]
# Imports preservados para uso futuro (job dedicado por órgão):
_UNUSED_BY_DESIGN = (
    fetch_contratos_municipio,
    fetch_licitacoes_municipio,
    fetch_cartao_municipio,
    fetch_viagens_municipio,
)


async def _collect_from_source(
    client: TransparenciaClient,
    fetcher,
    codigo_ibge: str,
    ano_mes: str,
) -> list[Contrato]:
    out: list[Contrato] = []
    async for c in fetcher(client, codigo_ibge=codigo_ibge, ano_mes=ano_mes):
        out.append(c)
    return out


async def _collect_all(
    api_key: str,
    codigo_ibge: str,
    ano_mes: str,
    *,
    rate_per_minute: int,
    base_url: str,
) -> tuple[list[Contrato], dict[str, int]]:
    """Coleta de todas as sources em sequência. Retorna (contratos, contagem_por_source)."""
    contratos: list[Contrato] = []
    contagem: dict[str, int] = {}
    async with TransparenciaClient(
        api_key=api_key, rate_per_minute=rate_per_minute, base_url=base_url
    ) as c:
        for nome, fetcher in SOURCES:
            try:
                rows = await _collect_from_source(c, fetcher, codigo_ibge, ano_mes)
                contratos.extend(rows)
                contagem[nome] = len(rows)
                print(f"[sync] {nome} {codigo_ibge} {ano_mes}: {len(rows)} registros", flush=True)
            except Exception as e:  # noqa: BLE001
                print(f"[sync] {nome} {codigo_ibge} {ano_mes} FALHOU: {e}", flush=True)
                traceback.print_exc()
                contagem[nome] = 0
    return contratos, contagem


def sync_transferencias_mes(settings: Settings, codigo_ibge: str, ano_mes: str) -> int:
    """Sincroniza um município/mês: fetch (4 fontes) → Bronze R2 → Gold Postgres → agregações."""
    contratos, contagem = asyncio.run(
        _collect_all(
            settings.transparencia_api_key,
            codigo_ibge,
            ano_mes,
            rate_per_minute=settings.transparencia_rate_per_minute,
            base_url=settings.transparencia_base_url,
        )
    )
    if not contratos:
        return 0

    # Bronze (R2) — somente se R2 configurado
    if settings.r2_account_id and settings.r2_access_key_id:
        try:
            r2 = make_r2_client(
                settings.r2_account_id,
                settings.r2_access_key_id,
                settings.r2_secret_access_key,
            )
            blob = contratos_to_parquet_bytes(contratos)
            upload_bytes(
                r2,
                settings.r2_bucket_bronze,
                bronze_key_transferencias(codigo_ibge, ano_mes),
                blob,
                content_type="application/parquet",
            )
        except Exception as e:  # noqa: BLE001
            print(f"[sync] R2 upload falhou (continua sem bronze): {e}", flush=True)

    # Gold (Postgres) — empresas mínimas + contratos + agregações
    empresas_min = [
        Empresa(cnpj=c.cnpj_fornecedor, razao_social="")
        for c in contratos
        if c.cnpj_fornecedor
    ]
    pool = make_pool(settings.db_conninfo())
    try:
        with pool.connection() as conn:
            upsert_empresas(conn, empresas_min)
            n = upsert_contratos(conn, contratos)
            ano = int(ano_mes.split("-")[0])
            recompute_agregacoes_municipio(conn, codigo_ibge, ano)
    finally:
        pool.close()

    return n


def run_multiplas_cidades(
    settings: Settings, ibge_ids: list[str], ano_mes: str
) -> dict[str, int]:
    """Sincroniza vários municípios sequencialmente."""
    return {
        ibge: sync_transferencias_mes(settings, ibge, ano_mes) for ibge in ibge_ids
    }

"""Sync de dinheiro federal por município — orquestra múltiplas fontes da CGU.

Cada source é fail-soft: se um endpoint específico falhar (403, schema mudou),
loga e segue com os outros. Garante cobertura parcial mesmo com problemas
em um endpoint específico.
"""
from __future__ import annotations

import asyncio

import httpx

from olho_publico_etl import _log
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
from olho_publico_etl.sources.transparencia.coronavirus import (
    fetch_coronavirus_municipio,
)
from olho_publico_etl.sources.transparencia.emendas import fetch_emendas_municipio
from olho_publico_etl.sources.transparencia.empenhos import fetch_empenhos_municipio
from olho_publico_etl.sources.transparencia.licitacoes import fetch_licitacoes_municipio
from olho_publico_etl.sources.transparencia.recursos_recebidos import (
    fetch_recursos_municipio,
)
from olho_publico_etl.sources.transparencia.transferencias import (
    fetch_transferencias_municipio,
)
from olho_publico_etl.sources.transparencia.viagens import fetch_viagens_municipio
from olho_publico_etl.storage.r2 import make_r2_client, upload_bytes

from .recompute_agregacoes import recompute_agregacoes_municipio

# Sources que populam `contratos`. Cada uma é fail-soft.
SOURCES = [
    ("convenios", fetch_convenios_municipio),
    ("transferencias", fetch_transferencias_municipio),  # requer Gov.br Ouro
    ("emendas", fetch_emendas_municipio),
    ("empenhos", fetch_empenhos_municipio),  # requer Gov.br Ouro
    ("coronavirus", fetch_coronavirus_municipio),  # transferências COVID
    ("recursos_recebidos", fetch_recursos_municipio),  # alternativa a /transferencias
]
# Imports preservados (exigem codigoOrgao, fora do sync municipal):
_UNUSED_BY_DESIGN = (
    fetch_contratos_municipio,
    fetch_licitacoes_municipio,
    fetch_cartao_municipio,
    fetch_viagens_municipio,
)
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
) -> tuple[list[Contrato], dict[str, int], dict[str, str]]:
    """Coleta de todas as sources em sequência.

    Retorna (contratos, contagem_por_source, erros_por_source).
    erros_por_source: rótulo curto (ex.: "403", "400", "ERR") para agregação.
    """
    contratos: list[Contrato] = []
    contagem: dict[str, int] = {}
    erros: dict[str, str] = {}
    async with TransparenciaClient(
        api_key=api_key, rate_per_minute=rate_per_minute, base_url=base_url
    ) as c:
        for nome, fetcher in SOURCES:
            try:
                rows = await _collect_from_source(c, fetcher, codigo_ibge, ano_mes)
                contratos.extend(rows)
                contagem[nome] = len(rows)
            except httpx.HTTPStatusError as e:
                contagem[nome] = 0
                erros[nome] = str(e.response.status_code)
            except Exception as e:  # noqa: BLE001
                contagem[nome] = 0
                erros[nome] = type(e).__name__
    return contratos, contagem, erros


def sync_transferencias_mes(
    settings: Settings, codigo_ibge: str, ano_mes: str
) -> tuple[int, dict[str, str]]:
    """Sincroniza um município/mês: fetch → Bronze R2 → Gold Postgres → agregações.

    Retorna (n_contratos_upsertados, erros_por_source).
    """
    contratos, _, erros = asyncio.run(
        _collect_all(
            settings.transparencia_api_key,
            codigo_ibge,
            ano_mes,
            rate_per_minute=settings.transparencia_rate_per_minute,
            base_url=settings.transparencia_base_url,
        )
    )
    if not contratos:
        return 0, erros

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
            _log.warn("sync", f"R2 upload falhou (segue sem bronze): {e}")

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

    return n, erros


def run_multiplas_cidades(
    settings: Settings, ibge_ids: list[str], ano_mes: str
) -> tuple[dict[str, int], dict[str, int]]:
    """Sincroniza vários municípios sequencialmente.

    Retorna (contratos_por_cidade, erros_agregados_por_source).
    erros_agregados: nome_source -> n_cidades_que_falharam.
    Loga progresso a cada 100 cidades em listas grandes.
    """
    contratos_por_cidade: dict[str, int] = {}
    erros_agg: dict[str, int] = {}
    total = len(ibge_ids)
    log_every = 100 if total > 200 else max(total // 5, 1)

    for i, ibge in enumerate(ibge_ids, start=1):
        n, erros = sync_transferencias_mes(settings, ibge, ano_mes)
        contratos_por_cidade[ibge] = n
        for src in erros:
            erros_agg[src] = erros_agg.get(src, 0) + 1
        if total > 50 and i % log_every == 0:
            parcial = sum(contratos_por_cidade.values())
            _log.info(
                "sync",
                f"{ano_mes} progresso {i}/{total} cidades — {parcial} contratos até agora",
            )

    return contratos_por_cidade, erros_agg

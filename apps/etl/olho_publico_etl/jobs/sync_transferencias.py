from __future__ import annotations

import asyncio

from olho_publico_etl.config import Settings
from olho_publico_etl.db import make_pool
from olho_publico_etl.models import Empresa
from olho_publico_etl.pipeline.bronze import (
    bronze_key_transferencias,
    contratos_to_parquet_bytes,
)
from olho_publico_etl.pipeline.gold import upsert_contratos, upsert_empresas
from olho_publico_etl.sources.transparencia.client import TransparenciaClient
from olho_publico_etl.sources.transparencia.transferencias import (
    fetch_transferencias_municipio,
)
from olho_publico_etl.storage.r2 import make_r2_client, upload_bytes

from .recompute_agregacoes import recompute_agregacoes_municipio


async def _collect_contratos(
    api_key: str, codigo_ibge: str, ano_mes: str, *, rate_per_minute: int
) -> list:
    async with TransparenciaClient(api_key=api_key, rate_per_minute=rate_per_minute) as c:
        out = []
        async for contrato in fetch_transferencias_municipio(
            c, codigo_ibge=codigo_ibge, ano_mes=ano_mes
        ):
            out.append(contrato)
        return out


def sync_transferencias_mes(settings: Settings, codigo_ibge: str, ano_mes: str) -> int:
    """Sincroniza um município/mês: fetch → Bronze R2 → Gold Postgres → agregações.

    Retorna a quantidade de contratos inseridos.
    """
    contratos = asyncio.run(
        _collect_contratos(
            settings.transparencia_api_key,
            codigo_ibge,
            ano_mes,
            rate_per_minute=settings.transparencia_rate_per_minute,
        )
    )
    if not contratos:
        return 0

    # Bronze (R2) — somente se R2 configurado
    if settings.r2_account_id and settings.r2_access_key_id:
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

    # Gold (Postgres)
    empresas_min = [
        Empresa(cnpj=c.cnpj_fornecedor, razao_social="")  # razão vazia preserva existente
        for c in contratos
        if c.cnpj_fornecedor
    ]
    pool = make_pool(settings.database_url)
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

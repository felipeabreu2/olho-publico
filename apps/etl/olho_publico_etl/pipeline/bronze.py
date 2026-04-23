from __future__ import annotations

import io
from collections.abc import Iterable

import polars as pl

from olho_publico_etl.models import Contrato


def contratos_to_parquet_bytes(rows: Iterable[Contrato]) -> bytes:
    """Serializa lista de Contrato em Parquet (bytes), schema plano."""
    records = [
        {
            "municipio_aplicacao_id": r.municipio_aplicacao_id,
            "cnpj_fornecedor": r.cnpj_fornecedor,
            "orgao_contratante": r.orgao_contratante,
            "objeto": r.objeto,
            "valor": str(r.valor),  # preserva precisão
            "data_assinatura": r.data_assinatura.isoformat(),
            "modalidade_licitacao": r.modalidade_licitacao,
            "fonte": r.fonte,
            "dados_originais_url": r.dados_originais_url,
        }
        for r in rows
    ]
    df = pl.DataFrame(records)
    buf = io.BytesIO()
    df.write_parquet(buf, compression="snappy")
    return buf.getvalue()


def bronze_key_transferencias(codigo_ibge: str, ano_mes: str) -> str:
    """Ex: bronze/transferencias/3550308/2025-01.parquet"""
    return f"bronze/transferencias/{codigo_ibge}/{ano_mes}.parquet"

import io
from datetime import date
from decimal import Decimal

import polars as pl

from olho_publico_etl.models import Contrato
from olho_publico_etl.pipeline.bronze import contratos_to_parquet_bytes


def test_contratos_to_parquet_roundtrip():
    rows = [
        Contrato(
            municipio_aplicacao_id="3550308",
            cnpj_fornecedor="12345678000190",
            orgao_contratante="Governo Federal",
            objeto="Repasse SUS",
            valor=Decimal("1000.50"),
            data_assinatura=date(2025, 1, 1),
            fonte="portal_transparencia",
        )
    ]
    blob = contratos_to_parquet_bytes(rows)
    df = pl.read_parquet(io.BytesIO(blob))
    assert df.height == 1
    assert df["cnpj_fornecedor"][0] == "12345678000190"
    assert df["municipio_aplicacao_id"][0] == "3550308"

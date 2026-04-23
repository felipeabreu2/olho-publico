from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock

from olho_publico_etl.models import Contrato, Empresa, Municipio
from olho_publico_etl.pipeline.gold import upsert_contratos, upsert_empresas, upsert_municipios


def _fake_conn():
    conn = MagicMock()
    cur = conn.cursor.return_value.__enter__.return_value
    cur.fetchone.return_value = (0,)
    return conn, cur


def test_upsert_municipios_executa_uma_query_por_batch():
    conn, cur = _fake_conn()
    m = [Municipio(id_ibge="3550308", nome="São Paulo", slug="sao-paulo", uf="SP")]
    upsert_municipios(conn, m)
    assert cur.executemany.called
    sql = cur.executemany.call_args.args[0]
    assert "INSERT INTO municipios" in sql
    assert "ON CONFLICT" in sql


def test_upsert_empresas_minimo():
    conn, cur = _fake_conn()
    e = [Empresa(cnpj="12345678000190", razao_social="X Ltda")]
    upsert_empresas(conn, e)
    cur.executemany.assert_called_once()
    sql = cur.executemany.call_args.args[0]
    assert "INSERT INTO empresas" in sql
    assert "ON CONFLICT (cnpj) DO UPDATE" in sql


def test_upsert_contratos_insert_simples():
    conn, cur = _fake_conn()
    c = [Contrato(
        municipio_aplicacao_id="3550308",
        cnpj_fornecedor="12345678000190",
        orgao_contratante="Governo Federal",
        objeto="x",
        valor=Decimal("100"),
        data_assinatura=date(2025, 1, 1),
        fonte="portal_transparencia",
    )]
    upsert_contratos(conn, c)
    cur.executemany.assert_called_once()
    sql = cur.executemany.call_args.args[0]
    assert "INSERT INTO contratos" in sql

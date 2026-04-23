from unittest.mock import MagicMock

from olho_publico_etl.jobs.recompute_agregacoes import recompute_agregacoes_municipio


def test_recompute_executa_sql_de_agregacao_e_upsert():
    conn = MagicMock()
    cur = conn.cursor.return_value.__enter__.return_value
    cur.fetchone.return_value = (0, 0, 0, 0)
    cur.fetchall.return_value = []

    recompute_agregacoes_municipio(conn, municipio_id="3550308", ano=2025)

    calls = cur.execute.call_args_list
    sqls = [c.args[0] for c in calls]
    joined = " ".join(sqls)

    assert "SUM(valor)" in joined or "sum(valor)" in joined
    assert "agregacoes_municipio" in joined
    assert "municipio_aplicacao_id" in joined

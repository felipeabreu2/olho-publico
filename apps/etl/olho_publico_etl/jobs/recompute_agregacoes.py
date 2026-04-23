from __future__ import annotations

import json

_TOTALS_SQL = """
SELECT
    COALESCE(SUM(valor) FILTER (WHERE fonte = 'portal_transparencia'), 0) AS total_federais,
    COUNT(*)           FILTER (WHERE fonte = 'portal_transparencia')    AS qtd_federais,
    COALESCE(SUM(valor) FILTER (WHERE fonte LIKE 'prefeitura_%%'), 0)   AS total_prefeitura,
    COUNT(*)           FILTER (WHERE fonte LIKE 'prefeitura_%%')        AS qtd_prefeitura
FROM contratos
WHERE municipio_aplicacao_id = %s
  AND EXTRACT(YEAR FROM data_assinatura) = %s;
"""

_TOP_FORNECEDORES_SQL = """
SELECT
    c.cnpj_fornecedor,
    COALESCE(e.razao_social, '—') AS razao_social,
    COUNT(*)             AS total_contratos,
    SUM(c.valor)::text   AS valor_total
FROM contratos c
LEFT JOIN empresas e ON e.cnpj = c.cnpj_fornecedor
WHERE c.municipio_aplicacao_id = %s
  AND EXTRACT(YEAR FROM c.data_assinatura) = %s
  AND c.cnpj_fornecedor IS NOT NULL
GROUP BY c.cnpj_fornecedor, e.razao_social
ORDER BY SUM(c.valor) DESC
LIMIT 10;
"""

_UPSERT_AGREGACAO_SQL = """
INSERT INTO agregacoes_municipio (
    municipio_id, ano_referencia,
    total_contratos_federais, total_contratos_prefeitura,
    qtd_contratos_federais, qtd_contratos_prefeitura,
    top_fornecedores, gastos_por_area, comparacao_similares,
    atualizado_em
) VALUES (
    %s, %s, %s, %s, %s, %s, %s::jsonb, %s::jsonb, %s::jsonb, NOW()
)
ON CONFLICT (municipio_id, ano_referencia) DO UPDATE
SET total_contratos_federais = EXCLUDED.total_contratos_federais,
    total_contratos_prefeitura = EXCLUDED.total_contratos_prefeitura,
    qtd_contratos_federais = EXCLUDED.qtd_contratos_federais,
    qtd_contratos_prefeitura = EXCLUDED.qtd_contratos_prefeitura,
    top_fornecedores = EXCLUDED.top_fornecedores,
    gastos_por_area = EXCLUDED.gastos_por_area,
    comparacao_similares = EXCLUDED.comparacao_similares,
    atualizado_em = NOW();
"""


def recompute_agregacoes_municipio(conn, municipio_id: str, ano: int) -> None:
    """Recomputa a linha em agregacoes_municipio para (municipio_id, ano).

    Em P2: totals + top fornecedores. Gastos_por_area e comparacao_similares
    ficam como listas vazias — entram em planos posteriores.
    """
    with conn.cursor() as cur:
        cur.execute(_TOTALS_SQL, (municipio_id, ano))
        row = cur.fetchone()
        total_fed, qtd_fed, total_pref, qtd_pref = row if row else (0, 0, 0, 0)

        cur.execute(_TOP_FORNECEDORES_SQL, (municipio_id, ano))
        top_rows = cur.fetchall()
        top = [
            {
                "cnpj": r[0],
                "razaoSocial": r[1],
                "totalContratos": int(r[2]),
                "valorTotal": str(r[3]),
            }
            for r in top_rows
        ]

        cur.execute(
            _UPSERT_AGREGACAO_SQL,
            (
                municipio_id,
                ano,
                str(total_fed),
                str(total_pref),
                int(qtd_fed),
                int(qtd_pref),
                json.dumps(top),
                json.dumps([]),
                json.dumps([]),
            ),
        )
    conn.commit()

from __future__ import annotations

import json
from collections.abc import Iterable

from olho_publico_etl.models import Contrato, Empresa, Municipio

_MUNICIPIOS_SQL = """
INSERT INTO municipios (id_ibge, nome, slug, uf, cobertura_prefeitura)
VALUES (%(id_ibge)s, %(nome)s, %(slug)s, %(uf)s, %(cobertura_prefeitura)s)
ON CONFLICT (id_ibge) DO UPDATE
SET nome = EXCLUDED.nome,
    slug = EXCLUDED.slug,
    uf = EXCLUDED.uf,
    atualizado_em = NOW();
"""


def upsert_municipios(conn, municipios: Iterable[Municipio]) -> int:
    params = [
        {
            "id_ibge": m.id_ibge,
            "nome": m.nome,
            "slug": m.slug,
            "uf": m.uf,
            "cobertura_prefeitura": m.cobertura_prefeitura,
        }
        for m in municipios
    ]
    if not params:
        return 0
    with conn.cursor() as cur:
        cur.executemany(_MUNICIPIOS_SQL, params)
    conn.commit()
    return len(params)


_EMPRESAS_SQL = """
INSERT INTO empresas (cnpj, razao_social, flags)
VALUES (%(cnpj)s, %(razao_social)s, %(flags)s::jsonb)
ON CONFLICT (cnpj) DO UPDATE
SET razao_social = COALESCE(NULLIF(EXCLUDED.razao_social, ''), empresas.razao_social),
    atualizado_em = NOW();
"""


def upsert_empresas(conn, empresas: Iterable[Empresa]) -> int:
    params = [
        {
            "cnpj": e.cnpj,
            "razao_social": e.razao_social,
            "flags": json.dumps(e.flags),
        }
        for e in empresas
    ]
    if not params:
        return 0
    with conn.cursor() as cur:
        cur.executemany(_EMPRESAS_SQL, params)
    conn.commit()
    return len(params)


_CONTRATOS_SQL = """
INSERT INTO contratos (
    municipio_aplicacao_id, cnpj_fornecedor, orgao_contratante, objeto,
    valor, data_assinatura, modalidade_licitacao, fonte, dados_originais_url
) VALUES (
    %(municipio_aplicacao_id)s, %(cnpj_fornecedor)s, %(orgao_contratante)s, %(objeto)s,
    %(valor)s, %(data_assinatura)s, %(modalidade_licitacao)s, %(fonte)s, %(dados_originais_url)s
);
"""


def upsert_contratos(conn, contratos: Iterable[Contrato]) -> int:
    params = [
        {
            "municipio_aplicacao_id": c.municipio_aplicacao_id,
            "cnpj_fornecedor": c.cnpj_fornecedor,
            "orgao_contratante": c.orgao_contratante,
            "objeto": c.objeto,
            "valor": str(c.valor),
            "data_assinatura": c.data_assinatura,
            "modalidade_licitacao": c.modalidade_licitacao,
            "fonte": c.fonte,
            "dados_originais_url": c.dados_originais_url,
        }
        for c in contratos
    ]
    if not params:
        return 0
    with conn.cursor() as cur:
        cur.executemany(_CONTRATOS_SQL, params)
    conn.commit()
    return len(params)

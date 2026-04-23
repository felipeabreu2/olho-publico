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


# ─── Sanções (CEIS/CNEP) ─────────────────────────────────────────────
_SANCOES_SQL = """
INSERT INTO sancoes (
    cnpj, tipo_sancao, orgao_sancionador, data_inicio, data_fim, motivo, fonte_url
) VALUES (
    %(cnpj)s, %(tipo_sancao)s, %(orgao_sancionador)s,
    %(data_inicio)s, %(data_fim)s, %(motivo)s, %(fonte_url)s
)
ON CONFLICT DO NOTHING;
"""


def upsert_sancoes(conn, sancoes) -> int:
    """Insere sanções; ignora duplicatas via ON CONFLICT."""
    params = [
        {
            "cnpj": s.cnpj,
            "tipo_sancao": s.tipo_sancao,
            "orgao_sancionador": s.orgao_sancionador,
            "data_inicio": s.data_inicio,
            "data_fim": s.data_fim,
            "motivo": s.motivo,
            "fonte_url": s.fonte_url,
        }
        for s in sancoes
    ]
    if not params:
        return 0
    with conn.cursor() as cur:
        cur.executemany(_SANCOES_SQL, params)
    conn.commit()
    return len(params)


# ─── Programas sociais ────────────────────────────────────────────────
_PROGRAMAS_SOCIAIS_SQL = """
INSERT INTO programas_sociais (
    municipio_id, programa, ano_mes,
    qtd_beneficiarios, valor_total, valor_medio_beneficiario, fonte
) VALUES (
    %(municipio_id)s, %(programa)s, %(ano_mes)s,
    %(qtd_beneficiarios)s, %(valor_total)s, %(valor_medio_beneficiario)s, 'portal_transparencia'
)
ON CONFLICT (municipio_id, programa, ano_mes) DO UPDATE
SET qtd_beneficiarios = EXCLUDED.qtd_beneficiarios,
    valor_total = EXCLUDED.valor_total,
    valor_medio_beneficiario = EXCLUDED.valor_medio_beneficiario;
"""


def upsert_programas_sociais(conn, registros) -> int:
    params = [
        {
            "municipio_id": r.municipio_id,
            "programa": r.programa,
            "ano_mes": r.ano_mes,
            "qtd_beneficiarios": r.qtd_beneficiarios,
            "valor_total": str(r.valor_total),
            "valor_medio_beneficiario": (
                str(r.valor_medio_beneficiario) if r.valor_medio_beneficiario else None
            ),
        }
        for r in registros
    ]
    if not params:
        return 0
    with conn.cursor() as cur:
        cur.executemany(_PROGRAMAS_SOCIAIS_SQL, params)
    conn.commit()
    return len(params)


# ─── PEP (Pessoas Politicamente Expostas) ────────────────────────────
_PEP_SQL = """
INSERT INTO pessoas_pep (cpf_mascarado, nome, cargo, orgao, data_inicio, data_fim)
VALUES (%(cpf_mascarado)s, %(nome)s, %(cargo)s, %(orgao)s, %(data_inicio)s, %(data_fim)s)
ON CONFLICT DO NOTHING;
"""


def upsert_pep(conn, registros) -> int:
    params = [
        {
            "cpf_mascarado": r.cpf_mascarado,
            "nome": r.nome,
            "cargo": r.cargo,
            "orgao": r.orgao,
            "data_inicio": r.data_inicio,
            "data_fim": r.data_fim,
        }
        for r in registros
    ]
    if not params:
        return 0
    with conn.cursor() as cur:
        cur.executemany(_PEP_SQL, params)
    conn.commit()
    return len(params)

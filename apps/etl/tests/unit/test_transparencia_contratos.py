from olho_publico_etl.sources.transparencia.contratos import parse_contratos_payload


def test_parse_basico():
    payload = [{
        "id": 1,
        "dataAssinatura": "2026-01-15",
        "valorInicialCompra": 1234567.89,
        "fornecedor": {
            "nome": "CONSTRUTORA XYZ S.A.",
            "cnpjFormatado": "12.345.678/0001-90",
        },
        "objeto": "Pavimentação de via urbana — Av. Brasil",
        "orgao": {"nome": "Ministério da Infraestrutura"},
        "modalidadeCompra": {"descricao": "Pregão Eletrônico"},
        "unidadeGestora": {"municipio": {"codigoIbge": "3550308"}},
    }]
    rows = list(parse_contratos_payload(payload))
    assert len(rows) == 1
    r = rows[0]
    assert r.cnpj_fornecedor == "12345678000190"
    assert r.municipio_aplicacao_id == "3550308"
    assert "[CONTRATO]" in r.objeto
    assert "Pavimentação" in r.objeto
    assert r.modalidade_licitacao == "Pregão Eletrônico"


def test_parse_pula_sem_municipio_em_qualquer_path():
    assert list(parse_contratos_payload([{
        "fornecedor": {"cnpjFormatado": "12.345.678/0001-90"},
        "objeto": "x", "valorInicialCompra": 100,
    }])) == []


def test_parse_extrai_municipio_de_path_alternativo():
    payload = [{
        "id": 1,
        "valorInicialCompra": 1000,
        "fornecedor": {"cnpjFormatado": "12.345.678/0001-90"},
        "municipio": {"codigoIbge": "3304557"},
        "objeto": "Outro contrato",
        "dataAssinatura": "2026-04-01",
    }]
    rows = list(parse_contratos_payload(payload))
    assert len(rows) == 1
    assert rows[0].municipio_aplicacao_id == "3304557"

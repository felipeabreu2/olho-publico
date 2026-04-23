from olho_publico_etl.sources.transparencia.emendas import parse_emendas_payload


def test_parse_basico():
    payload = [{
        "ano": 2026,
        "autor": "DEPUTADO FULANO DE TAL",
        "favorecido": {"cpfCnpj": "12.345.678/0001-90"},
        "localidadeDoGasto": {"codigoIbge": "3550308"},
        "valorEmpenhado": 500000.00,
        "valorPago": 250000.00,
        "funcao": {"descricao": "Saúde"},
        "subfuncao": {"descricao": "Atenção Básica"},
    }]
    rows = list(parse_emendas_payload(payload))
    assert len(rows) == 1
    r = rows[0]
    assert r.cnpj_fornecedor == "12345678000190"
    assert r.municipio_aplicacao_id == "3550308"
    assert "[EMENDA]" in r.objeto
    assert "DEPUTADO FULANO" in r.objeto
    assert "Saúde" in r.objeto
    assert str(r.valor) == "500000.0"
    assert r.modalidade_licitacao == "EMENDA"


def test_parse_pula_sem_cnpj():
    assert list(parse_emendas_payload([{
        "ano": 2026, "autor": "X",
        "favorecido": {"cpfCnpj": ""},
        "localidadeDoGasto": {"codigoIbge": "3550308"},
        "valorEmpenhado": 100,
    }])) == []

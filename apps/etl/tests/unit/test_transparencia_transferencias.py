from olho_publico_etl.sources.transparencia.transferencias import (
    parse_transferencias_payload,
)


def test_parse_basico():
    payload = [{
        "valor": 1500000.00,
        "mesAno": "2026-04",
        "favorecido": {
            "nome": "PREFEITURA MUNICIPAL DE SÃO PAULO",
            "codigoFormatado": "12.345.678/0001-90",
        },
        "municipio": {"codigoIBGE": "3550308"},
        "programa": {"descricao": "Programa Saúde da Família"},
        "acaoOrcamentaria": {"descricao": "Atenção Básica"},
        "linguagemCidada": "Repasse SUS",
    }]
    rows = list(parse_transferencias_payload(payload))
    assert len(rows) == 1
    r = rows[0]
    assert r.cnpj_fornecedor == "12345678000190"
    assert r.municipio_aplicacao_id == "3550308"
    assert "[TRANSFERÊNCIA]" in r.objeto
    assert "Programa Saúde da Família" in r.objeto
    assert float(r.valor) == 1500000.0
    assert r.data_assinatura.year == 2026
    assert r.data_assinatura.month == 4


def test_parse_pula_sem_cnpj():
    assert list(parse_transferencias_payload([{
        "valor": 100, "mesAno": "2026-01",
        "favorecido": {"codigoFormatado": ""},
        "municipio": {"codigoIBGE": "3550308"},
    }])) == []


def test_parse_pula_sem_municipio():
    assert list(parse_transferencias_payload([{
        "valor": 100, "mesAno": "2026-01",
        "favorecido": {"codigoFormatado": "12.345.678/0001-90"},
        "municipio": {},
    }])) == []

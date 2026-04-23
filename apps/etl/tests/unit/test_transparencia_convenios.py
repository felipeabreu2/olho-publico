import json
from pathlib import Path

from olho_publico_etl.sources.transparencia.convenios import parse_convenios_payload

FIXTURE = Path(__file__).parent.parent / "fixtures" / "transparencia_convenios.json"


def test_parse_gera_contratos_com_fonte_e_cnpj_limpo():
    payload = json.loads(FIXTURE.read_text())
    rows = list(parse_convenios_payload(payload))
    assert len(rows) == 2

    r = rows[0]
    assert r.fonte == "portal_transparencia"
    assert r.cnpj_fornecedor == "12345678000190"
    assert r.municipio_aplicacao_id == "3550308"
    assert r.orgao_contratante == "Ministério da Saúde"
    assert str(r.valor) == "1234567.89"
    assert "[CONVÊNIO]" in r.objeto
    assert "atenção básica" in r.objeto


def test_parse_ignora_registros_sem_cnpj():
    bad = [{
        "id": 1, "valor": 100,
        "convenente": {"cnpjFormatado": ""},
        "municipioConvenente": {"codigoIBGE": "3550308"},
        "dimConvenio": {"objeto": "p"}, "orgao": {"nome": "x"},
        "dataPublicacao": "2026-01-01",
    }]
    assert list(parse_convenios_payload(bad)) == []


def test_parse_ignora_registros_com_valor_zero():
    zero = [{
        "id": 1, "valor": 0,
        "convenente": {"cnpjFormatado": "12.345.678/0001-90"},
        "municipioConvenente": {"codigoIBGE": "3550308"},
        "dimConvenio": {"objeto": "x"}, "orgao": {"nome": "y"},
        "dataPublicacao": "2026-01-01",
    }]
    assert list(parse_convenios_payload(zero)) == []

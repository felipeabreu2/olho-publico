import json
from pathlib import Path

from olho_publico_etl.sources.ibge.municipios import parse_ibge_payload

FIXTURE = Path(__file__).parent.parent / "fixtures" / "ibge_municipios_sample.json"


def test_parse_retorna_municipio_com_slug_e_uf():
    payload = json.loads(FIXTURE.read_text())
    rows = list(parse_ibge_payload(payload))
    assert len(rows) == 2
    sp = rows[0]
    assert sp.id_ibge == "3550308"
    assert sp.nome == "São Paulo"
    assert sp.uf == "SP"
    assert sp.slug == "sao-paulo"
    assert sp.cobertura_prefeitura == "nenhuma"


def test_parse_id_ibge_como_string_7_digitos():
    payload = [{"id": 123, "nome": "X", "microrregiao": {"mesorregiao": {"UF": {"sigla": "SP"}}}}]
    rows = list(parse_ibge_payload(payload))
    assert rows[0].id_ibge == "0000123"

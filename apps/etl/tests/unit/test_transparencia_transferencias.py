import json
from pathlib import Path

from olho_publico_etl.sources.transparencia.transferencias import parse_transferencias_payload

FIXTURE = Path(__file__).parent.parent / "fixtures" / "transparencia_transferencias.json"


def test_parse_gera_contratos_com_fonte_e_cnpj_limpo():
    payload = json.loads(FIXTURE.read_text())
    rows = list(parse_transferencias_payload(payload))
    assert len(rows) == 2

    r = rows[0]
    assert r.fonte == "portal_transparencia"
    assert r.cnpj_fornecedor == "12345678000190"  # sem pontuação
    assert r.municipio_aplicacao_id == "3550308"
    assert r.orgao_contratante == "Governo Federal"
    assert str(r.valor) == "1234567.89"
    assert "Assistência Farmacêutica" in r.objeto


def test_parse_ignora_registros_sem_cnpj():
    bad = [{"id": 1, "mesAno": "2025-01", "valor": 100,
            "favorecido": {"nome": "X", "codigoFormatado": ""},
            "municipio": {"codigoIBGE": "3550308"},
            "programa": {"descricao": "p"}, "acaoOrcamentaria": {"descricao": "a"}}]
    assert list(parse_transferencias_payload(bad)) == []

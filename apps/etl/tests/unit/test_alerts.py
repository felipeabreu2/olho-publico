from olho_publico_etl.alerts.rules import (
    ALL_RULES,
    EmpresaFogueteRule,
)


def test_all_rules_present():
    codigos = {r.codigo for r in ALL_RULES}
    assert codigos == {
        "EMPRESA_FOGUETE",
        "DISPENSA_SUSPEITA",
        "SOCIO_SANCIONADO",
        "CRESCIMENTO_ANOMALO",
        "CONCENTRACAO",
        "DOADOR_BENEFICIADO",
    }


def test_empresa_foguete_metadata():
    r = EmpresaFogueteRule()
    assert r.codigo == "EMPRESA_FOGUETE"
    assert r.versao_atual == "1.0.0"
    assert r.severidade_padrao == "forte"
    assert "automatizado" in r.disclaimer

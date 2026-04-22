from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from olho_publico_etl.models import Alerta, Contrato, Empresa


def test_empresa_valida():
    e = Empresa(cnpj="12345678000190", razao_social="Teste S.A.")
    assert e.cnpj == "12345678000190"
    assert e.flags == {}


def test_empresa_cnpj_invalido_falha():
    with pytest.raises(ValidationError):
        Empresa(cnpj="123", razao_social="X")


def test_contrato_valida():
    c = Contrato(
        orgao_contratante="Prefeitura X",
        objeto="Pavimentação",
        valor=Decimal("12000000.00"),
        data_assinatura=date(2025, 6, 1),
        fonte="portal_transparencia",
    )
    assert c.valor == Decimal("12000000.00")


def test_alerta_severidade_validada():
    with pytest.raises(ValidationError):
        Alerta(tipo="X", severidade="invalido", evidencia={}, regra_versao="1.0.0")

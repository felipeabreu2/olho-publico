from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel

FonteContrato = Literal[
    "portal_transparencia",
    "compras_gov",
    "prefeitura_el",
    "prefeitura_ipm",
    "prefeitura_betha",
    "prefeitura_equiplano",
]


class Contrato(BaseModel):
    municipio_aplicacao_id: str | None = None
    cnpj_fornecedor: str | None = None
    orgao_contratante: str
    objeto: str
    valor: Decimal
    data_assinatura: date
    modalidade_licitacao: str | None = None
    fonte: FonteContrato
    dados_originais_url: str | None = None

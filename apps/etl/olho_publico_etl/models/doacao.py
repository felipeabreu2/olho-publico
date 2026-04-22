from decimal import Decimal

from pydantic import BaseModel


class Doacao(BaseModel):
    cnpj_doador: str | None = None
    cpf_doador_mascarado: str | None = None
    candidato_nome: str
    candidato_cargo: str
    partido: str | None = None
    valor: Decimal
    ano_eleicao: int
    municipio_id: str | None = None

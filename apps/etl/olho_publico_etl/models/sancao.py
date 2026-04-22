from datetime import date

from pydantic import BaseModel


class Sancao(BaseModel):
    cnpj: str
    tipo_sancao: str
    orgao_sancionador: str
    data_inicio: date
    data_fim: date | None = None
    motivo: str | None = None
    fonte_url: str | None = None

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

SeveridadeAlerta = Literal["info", "atencao", "forte"]


class Alerta(BaseModel):
    tipo: str
    severidade: SeveridadeAlerta
    municipio_id: str | None = None
    cnpj_envolvido: str | None = None
    evidencia: dict
    data_deteccao: datetime = Field(default_factory=datetime.utcnow)
    regra_versao: str

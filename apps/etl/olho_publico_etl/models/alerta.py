from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field

SeveridadeAlerta = Literal["info", "atencao", "forte"]


def _now_utc() -> datetime:
    return datetime.now(UTC)


class Alerta(BaseModel):
    tipo: str
    severidade: SeveridadeAlerta
    municipio_id: str | None = None
    cnpj_envolvido: str | None = None
    evidencia: dict
    data_deteccao: datetime = Field(default_factory=_now_utc)
    regra_versao: str

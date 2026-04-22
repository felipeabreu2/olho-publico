from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field

CoberturaPrefeitura = Literal["nenhuma", "parcial", "completa"]


def _now_utc() -> datetime:
    return datetime.now(UTC)


class Municipio(BaseModel):
    id_ibge: str = Field(min_length=7, max_length=7)
    nome: str
    slug: str
    uf: str = Field(min_length=2, max_length=2)
    populacao: int | None = None
    idh: float | None = None
    geometria: str | None = None
    prefeito_nome: str | None = None
    prefeito_partido: str | None = None
    cobertura_prefeitura: CoberturaPrefeitura = "nenhuma"
    erp_detectado: str | None = None
    atualizado_em: datetime = Field(default_factory=_now_utc)

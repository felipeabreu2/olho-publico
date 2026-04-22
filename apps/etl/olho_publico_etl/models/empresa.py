from datetime import UTC, date, datetime

from pydantic import BaseModel, Field


def _now_utc() -> datetime:
    return datetime.now(UTC)


class Empresa(BaseModel):
    cnpj: str = Field(min_length=14, max_length=14, pattern=r"^\d{14}$")
    razao_social: str
    nome_fantasia: str | None = None
    data_abertura: date | None = None
    situacao: str | None = None
    cnae_principal: str | None = None
    municipio_sede_id: str | None = None
    flags: dict[str, bool] = Field(default_factory=dict)
    atualizado_em: datetime = Field(default_factory=_now_utc)


class Socio(BaseModel):
    cnpj: str = Field(min_length=14, max_length=14)
    cpf_mascarado: str | None = None
    nome: str
    tipo: str | None = None
    data_entrada: date | None = None

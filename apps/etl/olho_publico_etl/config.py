from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql://postgres:postgres@localhost:5432/olho_publico"

    r2_account_id: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket_raw: str = "olho-publico-raw"
    r2_bucket_bronze: str = "olho-publico-bronze"
    r2_bucket_backups: str = "olho-publico-backups"

    transparencia_api_key: str = ""

    # Lista CSV de IDs IBGE para sync periódico (ex: "3550308,3304557")
    ibge_sync_list: str = "3550308"

    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()


def require_settings(*fields: str) -> None:
    """Raise RuntimeError se qualquer campo listado estiver vazio."""
    s = get_settings()
    missing = [f for f in fields if not getattr(s, f, None)]
    if missing:
        raise RuntimeError(
            f"Variáveis de ambiente obrigatórias ausentes: {', '.join(missing)}"
        )

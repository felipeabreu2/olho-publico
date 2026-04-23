from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # ── Postgres ──
    # Quando POSTGRES_USER/PASSWORD são fornecidos, conninfo é construído em
    # formato libpq keyword (não exige URL encoding de senhas com @/:/?/etc).
    # Caso contrário, usa database_url diretamente (compatibilidade).
    database_url: str = "postgresql://postgres:postgres@localhost:5432/olho_publico"
    postgres_user: str = ""
    postgres_password: str = ""
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_db: str = "olho_publico"

    def db_conninfo(self) -> str:
        """Retorna conninfo psycopg-compatível.

        Prefere libpq keyword format quando POSTGRES_USER/PASSWORD presentes
        (evita problemas de URL encoding em senhas com @, :, #, ?, & etc).
        """
        if self.postgres_user and self.postgres_password:
            return (
                f"host={self.postgres_host} port={self.postgres_port} "
                f"user={self.postgres_user} password={self.postgres_password} "
                f"dbname={self.postgres_db}"
            )
        return self.database_url

    r2_account_id: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket_raw: str = "olho-publico-raw"
    r2_bucket_bronze: str = "olho-publico-bronze"
    r2_bucket_backups: str = "olho-publico-backups"

    transparencia_api_key: str = ""
    # 400 = limite diurno padrão da CGU. 700 entre 00h-06h. 180 para APIs restritas.
    transparencia_rate_per_minute: int = 400

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

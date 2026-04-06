from enum import Enum
from functools import lru_cache
from pathlib import Path

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class Environment(str, Enum):
    development = "development"
    testing = "testing"
    production = "production"


class DatabaseBackend(str, Enum):
    mariadb = "mariadb"
    oracle = "oracle"
    sqlite = "sqlite"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Formateador de Polizas"
    app_version: str = "0.1.0"
    environment: Environment = Environment.development
    debug: bool = True

    host: str = "127.0.0.1"
    port: int = 8000

    database_backend: DatabaseBackend = DatabaseBackend.mariadb
    database_host: str = "127.0.0.1"
    database_port: int = 3306
    database_name: str = "formateador_polizas"
    database_user: str = "app_user"
    database_password: str = "change_me"
    database_echo: bool = False
    database_sqlite_path: str = str(BASE_DIR / "app.db")

    jwt_algorithm: str = "HS256"
    jwt_access_token_minutes: int = 30
    jwt_refresh_token_minutes: int = 10080
    jwt_secret_key: str = "change-me-in-env"
    jwt_issuer: str = "formateador-polizas"

    auth_bootstrap_admin: bool = True
    auth_bootstrap_admin_username: str = "admin"
    auth_bootstrap_admin_password: str = "admin123"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def database_driver(self) -> str:
        drivers = {
            DatabaseBackend.mariadb: "mysql+pymysql",
            DatabaseBackend.oracle: "oracle+oracledb",
            DatabaseBackend.sqlite: "sqlite",
        }
        return drivers[self.database_backend]

    @computed_field  # type: ignore[prop-decorator]
    @property
    def database_url(self) -> str:
        if self.database_backend == DatabaseBackend.sqlite:
            return f"sqlite:///{self.database_sqlite_path}"
        return (
            f"{self.database_driver}://{self.database_user}:{self.database_password}"
            f"@{self.database_host}:{self.database_port}/{self.database_name}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()

"""
Configuración centralizada del sistema — Pydantic Settings.

Todas las variables se cargan desde el entorno o desde un archivo .env.
Esto evita hardcodear credenciales y permite que cada participante
tenga su propia configuración local sin afectar al equipo.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración global de la aplicación, validada al arranque."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Aplicación ──────────────────────────────────────────────
    app_name: str = "Sistema de Reservas BoA"
    app_version: str = "2.0.0"
    app_env: Literal["development", "staging", "production"] = "development"
    debug: bool = Field(default=False, validation_alias="APP_DEBUG")
    demo_routes_enabled: bool = False
    auto_create_schema: bool = False
    read_mode: Literal["baseline", "refactored"] = "refactored"
    log_level: str = "INFO"
    api_v1_prefix: str = "/api/v1"

    # ── PostgreSQL ──────────────────────────────────────────────
    postgres_user: str = "boa_admin"
    postgres_password: str = "local-lab-only"
    postgres_db: str = "boa_reservas"
    postgres_host: str = "localhost"
    postgres_port: int = 5455
    database_url: str | None = None

    # ── Valkey / Redis (Caché) ──────────────────────────────────
    valkey_url: str = "redis://localhost:6379/0"
    cache_enabled: bool = False
    cache_ttl_seconds: int = Field(default=30, ge=1)

    # ── Seguridad ───────────────────────────────────────────────
    secret_key: str = "change-me-in-production-use-openssl-rand-hex-32"
    api_key: str = "dev-api-key-change-in-production"
    allowed_origins: str = "http://localhost:3000,http://localhost:8000"

    # ── Concurrencia (Simulación) ───────────────────────────────
    secure_lock_delay_seconds: float = Field(default=0, ge=0, le=60)
    insecure_delay_seconds: float = 0.5
    provisional_ttl_minutes: int = Field(default=10, ge=1)

    # ── Rate Limiting ───────────────────────────────────────────
    rate_limit_per_minute: int = 60

    @property
    def db_url(self) -> str:
        """Construye la URL de conexión a PostgreSQL."""
        if self.database_url:
            url = self.database_url
            if url.startswith("postgresql://"):
                url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
            return url
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def cors_origins(self) -> list[str]:
        """Lista de orígenes CORS permitidos."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    """Singleton de configuración cacheado."""
    return Settings()

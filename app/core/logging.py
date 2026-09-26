"""
Módulo de logging estructurado.

Configura el sistema de logging para toda la aplicación con formato
JSON en producción y formato legible en desarrollo.
"""

import logging
import sys

from app.core.config import get_settings


def setup_logging() -> None:
    """Configura el logging global de la aplicación."""
    settings = get_settings()

    log_format = (
        "%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s"
        if not settings.is_production
        else '{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","message":"%(message)s"}'
    )

    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format=log_format,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )

    # Reducir verbosidad de librerías externas
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO if settings.debug else logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Obtiene un logger con el nombre dado."""
    return logging.getLogger(f"boa.{name}")

"""Dependencias compartidas para inyección en los routers."""

from app.db.session import get_db

__all__ = ["get_db"]


def require_demo():
    """Administración destructiva y experimentos solo en desarrollo explícito."""
    from fastapi import HTTPException

    from app.core.config import get_settings

    settings = get_settings()
    if settings.app_env != "development" or not settings.demo_routes_enabled:
        raise HTTPException(status_code=404, detail="Ruta de laboratorio deshabilitada")

"""Dependencias compartidas para inyección en los routers."""

from app.db.session import get_db

__all__ = ["get_db"]

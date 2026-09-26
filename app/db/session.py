"""
Sesión de base de datos — SQLAlchemy.

Configura el engine, la sesión y la base declarativa.
Provee el generador get_db() para inyección de dependencias en FastAPI.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.core.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.db_url,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.debug and not settings.is_production,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Session:  # type: ignore[misc]
    """Generador de sesiones para inyección de dependencias de FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

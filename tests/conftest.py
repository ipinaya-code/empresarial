"""
Fixtures compartidos para todos los tests.

Provee:
- Sesión de base de datos de test (SQLite in-memory)
- Cliente HTTP de test (TestClient)
- Datos semilla preconfigurados

Las variables de entorno se configuran ANTES de importar la app
para que Pydantic Settings las tome correctamente.
"""

import os

# ── Configurar entorno ANTES de cualquier import de la app ────
os.environ["APP_ENV"] = "development"
os.environ["DEBUG"] = "true"
os.environ["SECURE_LOCK_DELAY_SECONDS"] = "1"
os.environ["INSECURE_DELAY_SECONDS"] = "0.1"
os.environ["PROVISIONAL_TTL_MINUTES"] = "1"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["VALKEY_URL"] = "redis://localhost:63999/0"  # Puerto inexistente a propósito

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Limpiar la caché de settings para que tome las nuevas env vars
from app.core.config import get_settings
get_settings.cache_clear()

from app.db.session import Base, get_db
from app.main import app


# ── Base de datos de test (SQLite in-memory) ──────────────────
SQLALCHEMY_TEST_URL = "sqlite://"

test_engine = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# SQLite no soporta enums nativos de PostgreSQL, este handler
# permite que funcione con nuestros Enum de SQLAlchemy
@event.listens_for(test_engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()


TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """Override de la dependencia de BD para tests."""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Sobreescribir la dependencia de BD ANTES de crear el client
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    """Crea/limpia las tablas antes de cada test."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client():
    """Cliente HTTP de test con BD aislada."""
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client


@pytest.fixture
def seeded_client(client):
    """Cliente HTTP con datos semilla precargados."""
    response = client.post("/admin/seed")
    assert response.status_code == 200
    return client


@pytest.fixture
def seed_data(client):
    """Datos de la respuesta del seed."""
    response = client.post("/admin/seed")
    assert response.status_code == 200
    return response.json()

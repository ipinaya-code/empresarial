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
os.environ["APP_DEBUG"] = "false"
os.environ["DEMO_ROUTES_ENABLED"] = "true"
os.environ["CACHE_ENABLED"] = "false"
os.environ["SECURE_LOCK_DELAY_SECONDS"] = "0"
os.environ["INSECURE_DELAY_SECONDS"] = "0.1"
os.environ["PROVISIONAL_TTL_MINUTES"] = "1"
os.environ["DATABASE_URL"] = os.getenv("TEST_DATABASE_URL", "sqlite:///./test.db")
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
SQLALCHEMY_TEST_URL = os.environ["DATABASE_URL"]
if SQLALCHEMY_TEST_URL.startswith("postgresql"):
    from sqlalchemy.engine import make_url

    if make_url(SQLALCHEMY_TEST_URL).database != "boa_test":
        raise RuntimeError("TEST_DATABASE_URL debe apuntar a una base descartable llamada boa_test")
    test_engine = create_engine(SQLALCHEMY_TEST_URL, pool_size=10, max_overflow=10)
else:
    if os.getenv("TEST_DATABASE_URL"):
        raise RuntimeError("TEST_DATABASE_URL requiere PostgreSQL; no se sustituye por SQLite")
    test_engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)

    @event.listens_for(test_engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        dbapi_conn.execute("PRAGMA foreign_keys=ON")


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
def setup_db(request):
    """Crea/limpia las tablas antes de cada test."""
    if request.node.get_closest_marker("browser"):
        yield
        return
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


@pytest.fixture
def db_session():
    with TestSessionLocal() as db:
        yield db


@pytest.fixture
def session_factory():
    return TestSessionLocal

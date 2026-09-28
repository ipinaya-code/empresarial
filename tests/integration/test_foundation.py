"""Regresiones de contratos y barreras del laboratorio."""

import pytest

from app.core.config import get_settings
from app.services.disponibilidad_service import consultar_disponibilidad


def test_baseline_refactored_same_contract(seed_data, db_session, monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "read_mode", "baseline")
    baseline = consultar_disponibilidad(db_session, seed_data["primer_vuelo_id"])
    monkeypatch.setattr(settings, "read_mode", "refactored")
    assert consultar_disponibilidad(db_session, seed_data["primer_vuelo_id"]) == baseline


@pytest.mark.parametrize(
    "path", ["/api/v1/admin/reset", "/admin/seed", "/reservar/inseguro", "/api/v1/reservar/expirar"]
)
def test_demo_routes_disabled(client, monkeypatch, path):
    monkeypatch.setattr(get_settings(), "demo_routes_enabled", False)
    result = client.post(path, json={"usuario_id": 1, "asiento_id": 1})
    assert result.status_code == 404


def test_production_blocks_demo_even_when_flag_enabled(client, monkeypatch):
    monkeypatch.setattr(get_settings(), "app_env", "production")
    assert client.post("/api/v1/admin/reset").status_code == 404


def test_readiness_returns_503_without_database(client, monkeypatch):
    from sqlalchemy.orm import Session

    def fail(*args, **kwargs):
        raise RuntimeError("sensitive connection detail")

    monkeypatch.setattr(Session, "execute", fail)
    result = client.get("/api/v1/health/ready")
    assert result.status_code == 503
    assert "sensitive" not in result.text

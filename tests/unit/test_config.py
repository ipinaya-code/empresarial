"""La configuración propia no debe colisionar con DEBUG del sistema anfitrión."""

from app.core.config import Settings


def test_app_debug_ignores_unrelated_debug(monkeypatch):
    monkeypatch.setenv("DEBUG", "release")
    monkeypatch.setenv("APP_DEBUG", "false")
    assert Settings(_env_file=None).debug is False
    monkeypatch.setenv("APP_DEBUG", "true")
    assert Settings(_env_file=None).debug is True

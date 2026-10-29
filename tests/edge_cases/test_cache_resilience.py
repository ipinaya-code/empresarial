"""Tests de resiliencia y degradación elegante de la caché Valkey/Redis."""

from unittest.mock import MagicMock, patch

import pytest

from app.db.cache import cache_delete, cache_flush, cache_get, cache_set


class TestCacheResilience:
    """Verifica que el sistema sea tolerante a fallos y maneje la degradación de caché."""

    def test_cache_desactivada_retorna_valores_seguros(self):
        """Con la caché desactivada por defecto en settings, las operaciones son no-op seguras."""
        with patch("app.db.cache.get_valkey", return_value=None):
            assert cache_get("clave_prueba") is None
            assert cache_set("clave_prueba", {"dato": 123}) is False
            assert cache_delete("clave_prueba") is False
            assert cache_flush() is False

    def test_cache_tolerancia_a_errores_de_conexion(self):
        """Si Redis/Valkey arroja un error de conexión, el servicio captura la excepción."""
        mock_client = MagicMock()
        mock_client.get.side_effect = Exception("Conexión rechazada a Redis")
        mock_client.setex.side_effect = Exception("Conexión rechazada a Redis")
        mock_client.delete.side_effect = Exception("Conexión rechazada a Redis")
        mock_client.flushdb.side_effect = Exception("Conexión rechazada a Redis")

        with patch("app.db.cache.get_valkey", return_value=mock_client):
            assert cache_get("clave") is None
            assert cache_set("clave", "valor") is False
            assert cache_delete("clave") is False
            assert cache_flush() is False

    def test_health_ready_con_cache_activa_y_disponible(self, client):
        mock_valkey = MagicMock()
        mock_valkey.ping.return_value = True

        with patch("app.api.v1.health.get_settings") as mock_settings:
            mock_settings.return_value.cache_enabled = True
            with patch("app.api.v1.health.get_valkey", return_value=mock_valkey):
                response = client.get("/api/v1/health/ready")
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "ok"
                assert data["checks"]["valkey"] == "ok"

    def test_health_ready_con_cache_activa_pero_no_disponible_retorna_degradado(self, client):
        mock_valkey = MagicMock()
        mock_valkey.ping.side_effect = Exception("Redis offline")

        with patch("app.api.v1.health.get_settings") as mock_settings:
            mock_settings.return_value.cache_enabled = True
            with patch("app.api.v1.health.get_valkey", return_value=mock_valkey):
                response = client.get("/api/v1/health/ready")
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "degraded"
                assert data["checks"]["valkey"] == "unavailable"

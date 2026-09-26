"""
Tests de integración para los endpoints de reservas.

Estos tests ejecutan la API completa con una base de datos SQLite
de test para verificar el flujo end-to-end.
"""

import pytest


class TestHealthEndpoints:
    """Tests de los endpoints de health check."""

    def test_health_basic(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "boa-reservas-api"


class TestAdminEndpoints:
    """Tests de los endpoints administrativos."""

    def test_seed_crea_datos(self, client):
        response = client.post("/admin/seed")
        assert response.status_code == 200
        data = response.json()
        assert "vuelos_creados" in data or "primer_vuelo_id" in data

    def test_seed_idempotente(self, client):
        """Llamar a seed dos veces no debe fallar."""
        client.post("/admin/seed")
        response = client.post("/admin/seed")
        assert response.status_code == 200

    def test_reset_limpia_reservas(self, client):
        client.post("/admin/seed")
        response = client.post("/admin/reset")
        assert response.status_code == 200
        data = response.json()
        assert "reservas_eliminadas" in data


class TestReservaInsegura:
    """Tests del flujo de reserva sin control de concurrencia."""

    def test_reserva_insegura_exitosa(self, client):
        seed = client.post("/admin/seed").json()
        response = client.post("/reservar/inseguro", json={
            "usuario_id": seed["primer_usuario_id"],
            "asiento_id": seed["primer_asiento_id"],
        })
        assert response.status_code == 200
        data = response.json()
        assert data["estado"] == "confirmada"
        assert "codigo_reserva" in data

    def test_reserva_insegura_asiento_inexistente(self, client):
        client.post("/admin/seed")
        response = client.post("/reservar/inseguro", json={
            "usuario_id": 1,
            "asiento_id": 99999,
        })
        assert response.status_code == 404

    def test_reserva_insegura_usuario_inexistente(self, client):
        seed = client.post("/admin/seed").json()
        response = client.post("/reservar/inseguro", json={
            "usuario_id": 99999,
            "asiento_id": seed["primer_asiento_id"],
        })
        assert response.status_code == 404


class TestReservaSegura:
    """Tests del flujo de reserva con bloqueo pesimista."""

    def test_reserva_segura_exitosa(self, client):
        seed = client.post("/admin/seed").json()
        response = client.post("/reservar/seguro", json={
            "usuario_id": seed["primer_usuario_id"],
            "asiento_id": seed["primer_asiento_id"],
        })
        assert response.status_code == 200
        data = response.json()
        assert data["estado"] == "confirmada"
        assert data["codigo_reserva"].startswith("BOA-")

    def test_reserva_segura_asiento_no_disponible(self, client):
        """Reservar un asiento ya confirmado debe fallar."""
        seed = client.post("/admin/seed").json()
        # Primera reserva (exitosa)
        client.post("/reservar/seguro", json={
            "usuario_id": seed["primer_usuario_id"],
            "asiento_id": seed["primer_asiento_id"],
        })
        # Segunda reserva al mismo asiento (debe fallar)
        response = client.post("/reservar/seguro", json={
            "usuario_id": seed["primer_usuario_id"],
            "asiento_id": seed["primer_asiento_id"],
        })
        assert response.status_code in [400, 409]


class TestReservaProvisional:
    """Tests del flujo de reserva provisional con TTL."""

    def test_crear_reserva_provisional(self, client):
        seed = client.post("/admin/seed").json()
        response = client.post("/reservar/provisional", json={
            "usuario_id": seed["primer_usuario_id"],
            "asiento_id": seed["primer_asiento_id"],
        })
        assert response.status_code == 200
        data = response.json()
        assert data["estado"] == "pendiente"
        assert data["fecha_expiracion"] is not None

    def test_confirmar_reserva_provisional(self, client):
        seed = client.post("/admin/seed").json()
        # Crear provisional
        prov = client.post("/reservar/provisional", json={
            "usuario_id": seed["primer_usuario_id"],
            "asiento_id": seed["primer_asiento_id"],
        }).json()
        # Confirmar
        response = client.post(f"/reservar/{prov['id']}/confirmar")
        assert response.status_code == 200
        data = response.json()
        assert data["estado"] == "confirmada"

    def test_confirmar_reserva_inexistente(self, client):
        response = client.post("/reservar/99999/confirmar")
        assert response.status_code == 404

    def test_expirar_sin_reservas_pendientes(self, client):
        client.post("/admin/seed")
        response = client.post("/reservar/expirar")
        assert response.status_code == 200
        data = response.json()
        assert data["expiradas"] == 0


class TestValidacionPayload:
    """Tests de validación de datos de entrada."""

    def test_payload_vacio(self, client):
        response = client.post("/reservar/seguro", json={})
        assert response.status_code == 422

    def test_usuario_id_negativo(self, client):
        response = client.post("/reservar/seguro", json={
            "usuario_id": -1,
            "asiento_id": 1,
        })
        assert response.status_code == 422

    def test_asiento_id_cero(self, client):
        response = client.post("/reservar/seguro", json={
            "usuario_id": 1,
            "asiento_id": 0,
        })
        assert response.status_code == 422

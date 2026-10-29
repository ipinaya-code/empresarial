"""Tests de casos borde para consulta de disponibilidad de vuelos."""

from unittest.mock import patch

import pytest

from app.core.exceptions import VueloNoEncontradoError
from app.services.disponibilidad_service import consultar_disponibilidad


class TestVuelosDisponibilidad:
    """Pruebas adicionales sobre el endpoint y servicio de disponibilidad."""

    def test_disponibilidad_vuelo_existente(self, client):
        seed = client.post("/admin/seed").json()
        vuelo_id = seed["primer_vuelo_id"]

        response = client.get(f"/vuelos/{vuelo_id}/disponibilidad")
        assert response.status_code == 200
        data = response.json()

        assert data["vuelo_id"] == vuelo_id
        assert "codigo" in data
        assert "origen_iata" in data
        assert "destino_iata" in data
        assert data["capacidad_total"] > 0
        assert data["asientos_disponibles"] > 0
        assert data["asientos_ejecutiva_disponibles"] >= 0
        assert data["asientos_economica_disponibles"] >= 0
        assert len(data["asientos"]) == data["capacidad_total"]

    def test_disponibilidad_vuelo_inexistente_retorna_404(self, client):
        client.post("/admin/seed")
        response = client.get("/vuelos/99999/disponibilidad")
        assert response.status_code == 404
        assert "99999" in response.json()["detail"]

    def test_disponibilidad_se_actualiza_tras_reserva(self, client):
        seed = client.post("/admin/seed").json()
        vuelo_id = seed["primer_vuelo_id"]

        resp_antes = client.get(f"/vuelos/{vuelo_id}/disponibilidad").json()
        disponibles_antes = resp_antes["asientos_disponibles"]

        # Reservar un asiento
        client.post(
            "/reservar/seguro",
            json={
                "usuario_id": seed["primer_usuario_id"],
                "asiento_id": seed["primer_asiento_id"],
            },
        )

        resp_despues = client.get(f"/vuelos/{vuelo_id}/disponibilidad").json()
        disponibles_despues = resp_despues["asientos_disponibles"]

        assert disponibles_despues == disponibles_antes - 1

    def test_consultar_disponibilidad_cache_hit(self, db_session):
        fake_cache = {"vuelo_id": 1, "cached": True}
        with patch("app.services.disponibilidad_service.cache_get", return_value=fake_cache):
            resultado = consultar_disponibilidad(db_session, 1)
            assert resultado == fake_cache

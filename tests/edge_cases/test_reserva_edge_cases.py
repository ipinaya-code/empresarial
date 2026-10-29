"""Tests de casos borde para el ciclo de vida y concurrencia de reservas."""

import datetime

import pytest

from app.models.asiento import Asiento, EstadoAsiento
from app.models.reserva import EstadoReserva, Reserva


class TestReservaEdgeCases:
    """Casos borde en el flujo de reservas y expiración de TTL."""

    def test_confirmar_reserva_ya_expirada(self, client, db_session):
        """Si la reserva provisional expiró al momento de confirmar, debe cancelarse y liberar el asiento."""
        seed = client.post("/admin/seed").json()
        usuario_id = seed["primer_usuario_id"]
        asiento_id = seed["primer_asiento_id"]

        # Crear reserva provisional
        prov = client.post(
            "/reservar/provisional",
            json={"usuario_id": usuario_id, "asiento_id": asiento_id},
        ).json()
        reserva_id = prov["id"]

        # Forzar la fecha de expiración en el pasado
        reserva_db = db_session.query(Reserva).filter(Reserva.id == reserva_id).first()
        pasado = datetime.datetime.now(datetime.UTC).replace(tzinfo=None) - datetime.timedelta(minutes=15)
        reserva_db.fecha_expiracion = pasado
        db_session.commit()

        # Intentar confirmar
        response = client.post(f"/reservar/{reserva_id}/confirmar")
        assert response.status_code == 409
        assert "ha expirado" in response.json()["detail"]

        # Verificar que la reserva pasó a CANCELADA y el asiento a DISPONIBLE
        db_session.expire_all()
        reserva_actualizada = db_session.query(Reserva).filter(Reserva.id == reserva_id).first()
        asiento_actualizado = db_session.query(Asiento).filter(Asiento.id == asiento_id).first()

        assert reserva_actualizada.estado == EstadoReserva.CANCELADA
        assert asiento_actualizado.estado == EstadoAsiento.DISPONIBLE

    def test_confirmar_reserva_ya_confirmada_falla(self, client):
        """No se puede confirmar una reserva que ya fue confirmada previamente."""
        seed = client.post("/admin/seed").json()
        prov = client.post(
            "/reservar/provisional",
            json={"usuario_id": seed["primer_usuario_id"], "asiento_id": seed["primer_asiento_id"]},
        ).json()

        # Primera confirmación exitosa
        resp1 = client.post(f"/reservar/{prov['id']}/confirmar")
        assert resp1.status_code == 200

        # Segunda confirmación debe fallar por estado no pendiente
        resp2 = client.post(f"/reservar/{prov['id']}/confirmar")
        assert resp2.status_code == 409
        assert "pendiente" in resp2.json()["detail"]

    def test_reserva_provisional_sobre_asiento_no_disponible(self, client):
        """No se puede crear reserva provisional sobre un asiento ya ocupado."""
        seed = client.post("/admin/seed").json()
        asiento_id = seed["primer_asiento_id"]

        # Asiento ocupado mediante reserva segura
        client.post(
            "/reservar/seguro",
            json={"usuario_id": seed["primer_usuario_id"], "asiento_id": asiento_id},
        )

        # Intento de reserva provisional en el mismo asiento
        response = client.post(
            "/reservar/provisional",
            json={"usuario_id": seed["primer_usuario_id"], "asiento_id": asiento_id},
        )
        assert response.status_code == 409
        assert "no está disponible" in response.json()["detail"]

    def test_expirar_multiples_reservas_vencidas(self, client, db_session):
        """El endpoint de expiración masiva debe limpiar todas las reservas vencidas."""
        seed = client.post("/admin/seed").json()
        usuario_id = seed["primer_usuario_id"]

        # Obtener los dos primeros asientos disponibles
        asientos = db_session.query(Asiento).filter(Asiento.estado == EstadoAsiento.DISPONIBLE).limit(2).all()
        assert len(asientos) == 2
        asiento1_id, asiento2_id = asientos[0].id, asientos[1].id

        # Crear 2 reservas provisionales
        res1 = client.post(
            "/reservar/provisional",
            json={"usuario_id": usuario_id, "asiento_id": asiento1_id},
        ).json()
        res2 = client.post(
            "/reservar/provisional",
            json={"usuario_id": usuario_id, "asiento_id": asiento2_id},
        ).json()

        # Vencer ambas reservas
        pasado = datetime.datetime.now(datetime.UTC).replace(tzinfo=None) - datetime.timedelta(minutes=30)
        db_session.query(Reserva).filter(Reserva.id.in_([res1["id"], res2["id"]])).update(
            {"fecha_expiracion": pasado}, synchronize_session=False
        )
        db_session.commit()

        # Ejecutar endpoint de expiración
        resp_exp = client.post("/reservar/expirar")
        assert resp_exp.status_code == 200
        data = resp_exp.json()
        assert data["expiradas"] == 2

        # Verificar que ambos asientos volvieron a DISPONIBLE
        db_session.expire_all()
        a1 = db_session.query(Asiento).filter(Asiento.id == asiento1_id).first()
        a2 = db_session.query(Asiento).filter(Asiento.id == asiento2_id).first()
        assert a1.estado == EstadoAsiento.DISPONIBLE
        assert a2.estado == EstadoAsiento.DISPONIBLE

    def test_reserva_segura_asiento_inexistente(self, client):
        client.post("/admin/seed")
        resp = client.post("/reservar/seguro", json={"usuario_id": 1, "asiento_id": 99999})
        assert resp.status_code == 404

    def test_reserva_segura_usuario_inexistente(self, client):
        seed = client.post("/admin/seed").json()
        resp = client.post("/reservar/seguro", json={"usuario_id": 99999, "asiento_id": seed["primer_asiento_id"]})
        assert resp.status_code == 404

    def test_reserva_provisional_asiento_inexistente(self, client):
        client.post("/admin/seed")
        resp = client.post("/reservar/provisional", json={"usuario_id": 1, "asiento_id": 99999})
        assert resp.status_code == 404

    def test_reserva_provisional_usuario_inexistente(self, client):
        seed = client.post("/admin/seed").json()
        resp = client.post("/reservar/provisional", json={"usuario_id": 99999, "asiento_id": seed["primer_asiento_id"]})
        assert resp.status_code == 404

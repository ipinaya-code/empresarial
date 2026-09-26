"""
Test E2E: User Journey completo de reserva de vuelo BoA.

Simula el flujo real de un pasajero:
1. Consultar vuelos disponibles
2. Ver disponibilidad de asientos
3. Crear reserva provisional
4. Confirmar la reserva
5. Verificar que el asiento ya no está disponible
"""



class TestUserJourney:
    """Flujo end-to-end de un pasajero reservando un vuelo."""

    def test_flujo_completo_reserva_provisional(self, client):
        """
        Escenario: Un pasajero reserva un asiento paso a paso.

        1. Seed: Inicializar datos
        2. Consultar disponibilidad del vuelo
        3. Reservar provisionalmente un asiento
        4. Confirmar la reserva
        5. Verificar que el asiento ya no está disponible
        """
        # ── 1. Inicializar datos ──────────────────────────────
        seed = client.post("/admin/seed").json()
        assert seed["primer_vuelo_id"] is not None

        vuelo_id = seed["primer_vuelo_id"]
        asiento_id = seed["primer_asiento_id"]
        usuario_id = seed["primer_usuario_id"]

        # ── 2. Consultar disponibilidad ───────────────────────
        disp = client.get(f"/vuelos/{vuelo_id}/disponibilidad")
        assert disp.status_code == 200
        disp_data = disp.json()
        assert disp_data["asientos_disponibles"] > 0
        asientos_antes = disp_data["asientos_disponibles"]

        # ── 3. Reserva provisional ────────────────────────────
        prov = client.post(
            "/reservar/provisional",
            json={
                "usuario_id": usuario_id,
                "asiento_id": asiento_id,
            },
        )
        assert prov.status_code == 200
        prov_data = prov.json()
        assert prov_data["estado"] == "pendiente"
        reserva_id = prov_data["id"]

        # ── 4. Confirmar reserva ──────────────────────────────
        confirm = client.post(f"/reservar/{reserva_id}/confirmar")
        assert confirm.status_code == 200
        confirm_data = confirm.json()
        assert confirm_data["estado"] == "confirmada"

        # ── 5. Verificar que el asiento ya no está disponible ─
        disp2 = client.get(f"/vuelos/{vuelo_id}/disponibilidad")
        assert disp2.status_code == 200
        disp2_data = disp2.json()
        assert disp2_data["asientos_disponibles"] == asientos_antes - 1

    def test_flujo_reserva_segura_directa(self, client):
        """
        Escenario: Reserva directa sin paso provisional.
        """
        seed = client.post("/admin/seed").json()

        # Reserva directa segura
        res = client.post(
            "/reservar/seguro",
            json={
                "usuario_id": seed["primer_usuario_id"],
                "asiento_id": seed["primer_asiento_id"],
            },
        )
        assert res.status_code == 200
        data = res.json()
        assert data["estado"] == "confirmada"
        assert data["codigo_reserva"].startswith("BOA-")

    def test_flujo_doble_reserva_mismo_asiento(self, client):
        """
        Escenario: Dos pasajeros intentan reservar el mismo asiento.
        Solo uno debe tener éxito.
        """
        seed = client.post("/admin/seed").json()
        asiento_id = seed["primer_asiento_id"]

        # Pasajero 1: reserva exitosa
        res1 = client.post(
            "/reservar/seguro",
            json={
                "usuario_id": seed["primer_usuario_id"],
                "asiento_id": asiento_id,
            },
        )
        assert res1.status_code == 200

        # Pasajero 2: debe fallar
        res2 = client.post(
            "/reservar/seguro",
            json={
                "usuario_id": seed["primer_usuario_id"],
                "asiento_id": asiento_id,
            },
        )
        assert res2.status_code in [400, 409]

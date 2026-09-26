"""Tests unitarios para los modelos del sistema de reservas BoA."""

import pytest

from app.models.asiento import ClaseServicio, EstadoAsiento
from app.models.reserva import EstadoReserva


class TestEstadoAsiento:
    """Pruebas de la enumeración EstadoAsiento."""

    def test_valores_definidos(self):
        assert EstadoAsiento.DISPONIBLE.value == "disponible"
        assert EstadoAsiento.RESERVADO_PROVISIONAL.value == "reservado_provisional"
        assert EstadoAsiento.CONFIRMADO.value == "confirmado"
        assert EstadoAsiento.BLOQUEADO.value == "bloqueado"

    def test_total_estados(self):
        """Debe haber exactamente 4 estados de asiento."""
        assert len(EstadoAsiento) == 4


class TestEstadoReserva:
    """Pruebas de la enumeración EstadoReserva."""

    def test_valores_definidos(self):
        assert EstadoReserva.PENDIENTE.value == "pendiente"
        assert EstadoReserva.CONFIRMADA.value == "confirmada"
        assert EstadoReserva.CANCELADA.value == "cancelada"

    def test_total_estados(self):
        """Debe haber exactamente 3 estados de reserva."""
        assert len(EstadoReserva) == 3


class TestClaseServicio:
    """Pruebas de la enumeración ClaseServicio."""

    def test_valores_definidos(self):
        assert ClaseServicio.EJECUTIVA.value == "ejecutiva"
        assert ClaseServicio.ECONOMICA.value == "economica"

    def test_total_clases(self):
        """Debe haber exactamente 2 clases de servicio."""
        assert len(ClaseServicio) == 2

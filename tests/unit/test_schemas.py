"""Tests unitarios para los schemas de validación Pydantic."""

import pytest
from pydantic import ValidationError

from app.schemas.reserva import ReservaCreate


class TestReservaCreate:
    """Pruebas de validación del schema ReservaCreate."""

    def test_crear_reserva_valida(self):
        reserva = ReservaCreate(usuario_id=1, asiento_id=1)
        assert reserva.usuario_id == 1
        assert reserva.asiento_id == 1

    def test_usuario_id_debe_ser_positivo(self):
        with pytest.raises(ValidationError):
            ReservaCreate(usuario_id=0, asiento_id=1)

    def test_asiento_id_debe_ser_positivo(self):
        with pytest.raises(ValidationError):
            ReservaCreate(usuario_id=1, asiento_id=-1)

    def test_campos_obligatorios(self):
        with pytest.raises(ValidationError):
            ReservaCreate()

    def test_no_acepta_strings(self):
        with pytest.raises(ValidationError):
            ReservaCreate(usuario_id="abc", asiento_id=1)

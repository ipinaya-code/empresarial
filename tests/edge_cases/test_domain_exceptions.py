"""Tests para las excepciones del dominio y su mapeo a códigos HTTP."""

import pytest
from fastapi import HTTPException

from app.core.exceptions import (
    AsientoNoDisponibleError,
    AsientoNoEncontradoError,
    BoABaseException,
    DatosYaInicializadosError,
    ReservaActivaDuplicadaError,
    ReservaExpiradaError,
    ReservaNoEncontradaError,
    ReservaNoModificableError,
    UsuarioNoEncontradoError,
    VueloNoEncontradoError,
    boa_exception_to_http,
)


class TestDomainExceptions:
    """Verifica que cada error del negocio se traduzca al status HTTP correcto."""

    def test_excepciones_404_no_encontrado(self):
        casos = [
            (AsientoNoEncontradoError(12), 404, "Asiento con ID 12"),
            (UsuarioNoEncontradoError(34), 404, "Usuario con ID 34"),
            (VueloNoEncontradoError(56), 404, "Vuelo con ID 56"),
            (ReservaNoEncontradaError(78), 404, "Reserva con ID 78"),
        ]
        for exc, expected_status, text_snippet in casos:
            http_exc = boa_exception_to_http(exc)
            assert isinstance(http_exc, HTTPException)
            assert http_exc.status_code == expected_status
            assert text_snippet in http_exc.detail

    def test_excepciones_409_conflicto(self):
        casos = [
            (AsientoNoDisponibleError(99), 409, "Asiento 99 no está disponible"),
            (AsientoNoDisponibleError(), 409, "El asiento solicitado no está disponible"),
            (ReservaActivaDuplicadaError(), 409, "reserva activa"),
            (ReservaNoModificableError(10), 409, "pendiente"),
            (ReservaExpiradaError(20), 409, "ha expirado"),
            (DatosYaInicializadosError(), 409, "ya están inicializados"),
        ]
        for exc, expected_status, text_snippet in casos:
            http_exc = boa_exception_to_http(exc)
            assert isinstance(http_exc, HTTPException)
            assert http_exc.status_code == expected_status
            assert text_snippet in http_exc.detail

    def test_excepcion_base_default(self):
        base = BoABaseException(detail="Error genérico interno")
        assert base.status_code == 500
        http_exc = boa_exception_to_http(base)
        assert http_exc.status_code == 500
        assert http_exc.detail == "Error genérico interno"

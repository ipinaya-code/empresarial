"""Tests de validación para los schemas Pydantic de Usuario, Asiento y Vuelo."""

import pytest
from pydantic import ValidationError

from app.schemas.asiento import AsientoResponse
from app.schemas.usuario import UsuarioCreate, UsuarioResponse
from app.schemas.vuelo import VueloResponse


class TestSchemasValidation:
    """Verifica restricciones de validación en los modelos de datos."""

    def test_usuario_create_valido(self):
        user_data = {
            "nombre": "Carlos",
            "apellido": "Mendoza",
            "email": "carlos@example.com",
            "documento_numero": "6789012",
        }
        usuario = UsuarioCreate(**user_data)
        assert usuario.nombre == "Carlos"
        assert usuario.documento_tipo == "CI"
        assert usuario.nacionalidad == "BOL"

    def test_usuario_create_nombre_demasiado_corto(self):
        with pytest.raises(ValidationError):
            UsuarioCreate(
                nombre="A",  # Menor al min_length de 2
                apellido="Mendoza",
                email="carlos@example.com",
                documento_numero="6789012",
            )

    def test_usuario_create_documento_demasiado_corto(self):
        with pytest.raises(ValidationError):
            UsuarioCreate(
                nombre="Carlos",
                apellido="Mendoza",
                email="carlos@example.com",
                documento_numero="123",  # Menor al min_length de 5
            )

    def test_usuario_response_from_attributes(self):
        class ObjetoFicticio:
            id = 1
            nombre = "Ana"
            apellido = "Perez"
            email = "ana@test.com"
            documento_tipo = "CI"
            documento_numero = "1234567"
            telefono = None
            nacionalidad = "BOL"

        resp = UsuarioResponse.model_validate(ObjetoFicticio())
        assert resp.id == 1
        assert resp.nombre == "Ana"

    def test_asiento_response_from_attributes(self):
        class AsientoFicticio:
            id = 5
            numero = "1A"
            fila = 1
            columna = "A"
            clase = "ejecutiva"
            estado = "disponible"

        resp = AsientoResponse.model_validate(AsientoFicticio())
        assert resp.numero == "1A"
        assert resp.clase == "ejecutiva"

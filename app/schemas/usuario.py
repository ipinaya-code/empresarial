"""Schemas de validación para Usuario / Pasajero."""

from pydantic import BaseModel, ConfigDict, Field


class UsuarioCreate(BaseModel):
    """Datos requeridos para registrar un pasajero."""

    nombre: str = Field(..., min_length=2, max_length=100, examples=["Juan"])
    apellido: str = Field(..., min_length=2, max_length=100, examples=["Mamani"])
    email: str = Field(..., max_length=255, examples=["juan.mamani@gmail.com"])
    documento_tipo: str = Field(default="CI", examples=["CI", "PASAPORTE"])
    documento_numero: str = Field(..., min_length=5, max_length=20, examples=["12345678"])
    telefono: str | None = Field(default=None, examples=["+591 70012345"])
    nacionalidad: str = Field(default="BOL", min_length=3, max_length=3, examples=["BOL"])


class UsuarioResponse(BaseModel):
    """Datos de un pasajero en respuestas de la API."""

    id: int
    nombre: str
    apellido: str
    email: str
    documento_tipo: str
    documento_numero: str
    telefono: str | None = None
    nacionalidad: str

    model_config = ConfigDict(from_attributes=True)

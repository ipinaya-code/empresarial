"""Schemas de validación para Asiento."""

from pydantic import BaseModel


class AsientoResponse(BaseModel):
    """Datos de un asiento en respuestas de la API."""

    id: int
    numero: str
    fila: int
    columna: str
    clase: str
    estado: str

    class Config:
        from_attributes = True

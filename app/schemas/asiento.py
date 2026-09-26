"""Schemas de validación para Asiento."""

from pydantic import BaseModel, ConfigDict


class AsientoResponse(BaseModel):
    """Datos de un asiento en respuestas de la API."""

    id: int
    numero: str
    fila: int
    columna: str
    clase: str
    estado: str

    model_config = ConfigDict(from_attributes=True)

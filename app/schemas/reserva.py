"""Schemas de validación para Reserva."""

import datetime

from pydantic import BaseModel, Field


class ReservaCreate(BaseModel):
    """Datos requeridos para crear una reserva."""

    usuario_id: int = Field(..., gt=0, examples=[1])
    asiento_id: int = Field(..., gt=0, examples=[1])


class ReservaResponse(BaseModel):
    """Datos de una reserva en respuestas de la API."""

    id: int
    codigo_reserva: str
    usuario_id: int
    asiento_id: int
    estado: str
    fecha_reserva: datetime.datetime
    fecha_expiracion: datetime.datetime | None = None

    class Config:
        from_attributes = True

"""Schemas de validación para Vuelo."""

import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.asiento import AsientoResponse


class VueloResponse(BaseModel):
    """Datos de un vuelo en respuestas de la API."""

    id: int
    codigo: str
    origen_iata: str
    origen_nombre: str
    destino_iata: str
    destino_nombre: str
    fecha_salida: datetime.datetime
    fecha_llegada: datetime.datetime
    aeronave: str
    capacidad: int
    estado: str

    model_config = ConfigDict(from_attributes=True)


class VueloDisponibilidadResponse(BaseModel):
    """Resumen de disponibilidad de un vuelo — Endpoint CQRS de lectura."""

    vuelo_id: int
    codigo: str
    origen_iata: str = Field(..., examples=["VVI"])
    origen_nombre: str = Field(..., examples=["Viru Viru International"])
    destino_iata: str = Field(..., examples=["LPB"])
    destino_nombre: str = Field(..., examples=["El Alto International"])
    aeronave: str = Field(..., examples=["Boeing 737-300"])
    fecha_salida: datetime.datetime
    capacidad_total: int
    asientos_disponibles: int
    asientos_ejecutiva_disponibles: int
    asientos_economica_disponibles: int
    asientos: list[AsientoResponse]

    model_config = ConfigDict(from_attributes=True)

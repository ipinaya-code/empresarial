from pydantic import BaseModel, Field
import datetime
from app.models import EstadoAsiento, EstadoReserva

class ReservaCreate(BaseModel):
    usuario_id: int = Field(gt=0)
    asiento_id: int = Field(gt=0)

class ReservaResponse(BaseModel):
    id: int
    usuario_id: int
    asiento_id: int
    estado: EstadoReserva
    fecha_expiracion: datetime.datetime | None = None
    
    class Config:
        from_attributes = True

class AsientoResponse(BaseModel):
    id: int
    numero: str
    estado: EstadoAsiento

    class Config:
        from_attributes = True

class VueloDisponibilidadResponse(BaseModel):
    vuelo_id: int
    origen: str
    destino: str
    capacidad_total: int
    asientos_disponibles: int
    asientos: list[AsientoResponse]

    class Config:
        from_attributes = True

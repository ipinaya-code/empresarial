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

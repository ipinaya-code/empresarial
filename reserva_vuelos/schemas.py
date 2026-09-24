from pydantic import BaseModel
from typing import List, Optional
import datetime
from models import EstadoAsiento, EstadoReserva

class ReservaCreate(BaseModel):
    usuario_id: int
    asiento_id: int

class ReservaResponse(BaseModel):
    id: int
    usuario_id: int
    asiento_id: int
    estado: EstadoReserva
    
    class Config:
        from_attributes = True

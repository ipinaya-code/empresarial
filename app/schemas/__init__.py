"""
Schemas de validación Pydantic — Sistema de Reservas BoA.

Expone todos los schemas para importación directa:
    from app.schemas import ReservaCreate, VueloResponse, etc.
"""

from app.schemas.asiento import AsientoResponse
from app.schemas.reserva import ReservaCreate, ReservaResponse
from app.schemas.usuario import UsuarioCreate, UsuarioResponse
from app.schemas.vuelo import VueloDisponibilidadResponse, VueloResponse

__all__ = [
    "UsuarioCreate",
    "UsuarioResponse",
    "VueloResponse",
    "VueloDisponibilidadResponse",
    "AsientoResponse",
    "ReservaCreate",
    "ReservaResponse",
]

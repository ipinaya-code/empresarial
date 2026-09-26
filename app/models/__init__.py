"""
Modelos de base de datos del sistema de reservas BoA.

Expone todos los modelos y enumeraciones para importación directa:
    from app.models import Usuario, Vuelo, Asiento, Reserva
"""

from app.models.asiento import Asiento, EstadoAsiento
from app.models.reserva import EstadoReserva, Reserva
from app.models.usuario import Usuario
from app.models.vuelo import Vuelo

__all__ = [
    "Usuario",
    "Vuelo",
    "Asiento",
    "Reserva",
    "EstadoAsiento",
    "EstadoReserva",
]

"""
Módulo de compatibilidad con código legacy.

DEPRECADO: Usar directamente los nuevos módulos:
    from app.schemas.reserva import ReservaCreate, ReservaResponse
    from app.schemas.vuelo import VueloDisponibilidadResponse
    from app.schemas.asiento import AsientoResponse
"""

from app.schemas.asiento import AsientoResponse  # noqa: F401
from app.schemas.reserva import ReservaCreate, ReservaResponse  # noqa: F401
from app.schemas.vuelo import VueloDisponibilidadResponse  # noqa: F401

"""
Endpoints de Administración.

Endpoints para inicializar y resetear datos de demostración.
En producción, estos endpoints estarían protegidos con autenticación.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_demo
from app.services.seed_service import crear_datos_semilla, resetear_datos

router = APIRouter(dependencies=[Depends(require_demo)])


@router.post(
    "/seed",
    summary="Inicializar datos de demostración de BoA",
    description=(
        "Crea vuelos con rutas domésticas sintéticas (VVI↔LPB, VVI↔CBB, etc.), "
        "asientos con configuración Boeing 737-300 (ejecutiva + económica), "
        "y 20 pasajeros bolivianos simulados."
    ),
)
def seed(db: Session = Depends(get_db)):
    return crear_datos_semilla(db)


@router.post(
    "/reset",
    summary="Resetear reservas y liberar asientos",
    description=(
        "Elimina todas las reservas y libera todos los asientos para "
        "repetir las pruebas de concurrencia. No elimina vuelos ni usuarios."
    ),
)
def reset(db: Session = Depends(get_db)):
    return resetear_datos(db)

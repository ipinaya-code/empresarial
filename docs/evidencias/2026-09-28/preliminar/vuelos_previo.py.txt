"""
Endpoints de Vuelos (CQRS: Query Side — Lectura).

Estos endpoints son de solo lectura y no emiten bloqueos.
En producción, podrían dirigirse a una réplica de lectura
o alimentarse completamente desde Valkey.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.exceptions import BoABaseException, boa_exception_to_http
from app.services.disponibilidad_service import consultar_disponibilidad

router = APIRouter()


@router.get(
    "/{vuelo_id}/disponibilidad",
    summary="Consultar disponibilidad de asientos",
    description=(
        "Endpoint de lectura optimizado (CQRS: Query). "
        "Utiliza caché Valkey para reducir la carga en PostgreSQL. "
        "No emite bloqueos pesimistas. Retorna la disponibilidad "
        "separada por clase de servicio (ejecutiva y económica)."
    ),
)
def disponibilidad(vuelo_id: int, db: Session = Depends(get_db)):
    try:
        return consultar_disponibilidad(db, vuelo_id)
    except BoABaseException as e:
        raise boa_exception_to_http(e)

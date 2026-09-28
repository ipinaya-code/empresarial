"""
Endpoints de Reservas (CQRS: Command Side — Escritura).

Estos endpoints modifican el estado de la base de datos y utilizan
bloqueos pesimistas (SELECT FOR UPDATE) para prevenir condiciones de carrera.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_demo
from app.core.exceptions import BoABaseException, boa_exception_to_http
from app.schemas.reserva import ReservaCreate, ReservaResponse
from app.services.reserva_service import (
    confirmar_reserva,
    expirar_reservas,
    reservar_inseguro,
    reservar_provisional,
    reservar_seguro,
)

router = APIRouter()


@router.post(
    "/inseguro",
    dependencies=[Depends(require_demo)],
    response_model=ReservaResponse,
    summary="Reserva SIN control de concurrencia (demostración)",
    description=(
        "⚠️ Endpoint de demostración que muestra una condición de carrera. "
        "NO usa SELECT FOR UPDATE. Múltiples solicitudes simultáneas pueden "
        "leer el asiento como disponible antes de que alguna lo confirme."
    ),
)
def inseguro(reserva: ReservaCreate, db: Session = Depends(get_db)):
    try:
        return reservar_inseguro(db, reserva.usuario_id, reserva.asiento_id)
    except BoABaseException as e:
        raise boa_exception_to_http(e)


@router.post(
    "/seguro",
    response_model=ReservaResponse,
    summary="Reserva CON bloqueo pesimista (SELECT FOR UPDATE)",
    description=(
        "✅ Endpoint seguro que usa SELECT ... FOR UPDATE para bloquear la fila "
        "del asiento. La demora de demostración es configurable y está desactivada por defecto. "
        "Solo UNA solicitud puede confirmar; las demás esperan y reciben un error."
    ),
)
def seguro(reserva: ReservaCreate, db: Session = Depends(get_db)):
    try:
        return reservar_seguro(db, reserva.usuario_id, reserva.asiento_id)
    except BoABaseException as e:
        raise boa_exception_to_http(e)


@router.post(
    "/provisional",
    response_model=ReservaResponse,
    summary="Reserva provisional con TTL de laboratorio",
    description=(
        "Crea una reserva temporal (PENDIENTE) con un TTL de 10 minutos. "
        "El asiento pasa a RESERVADO_PROVISIONAL. El pasajero debe confirmar "
        "antes de que expire. El plazo es una decisión del prototipo."
    ),
)
def provisional(reserva: ReservaCreate, db: Session = Depends(get_db)):
    try:
        return reservar_provisional(db, reserva.usuario_id, reserva.asiento_id)
    except BoABaseException as e:
        raise boa_exception_to_http(e)


@router.post(
    "/{reserva_id}/confirmar",
    response_model=ReservaResponse,
    summary="Confirmar una reserva provisional",
    description=(
        "Confirma una reserva en estado PENDIENTE. Si la reserva ha expirado, "
        "se cancela automáticamente y el asiento vuelve a estar disponible."
    ),
)
def confirmar(reserva_id: int, db: Session = Depends(get_db)):
    try:
        return confirmar_reserva(db, reserva_id)
    except BoABaseException as e:
        raise boa_exception_to_http(e)


@router.post(
    "/expirar",
    dependencies=[Depends(require_demo)],
    summary="Expirar reservas provisionales vencidas",
    description=(
        "Cancela todas las reservas provisionales cuyo TTL ha expirado "
        "y libera los asientos asociados. En producción, esto sería "
        "ejecutado por un cron job o un worker en segundo plano."
    ),
)
def expirar(db: Session = Depends(get_db)):
    return expirar_reservas(db)

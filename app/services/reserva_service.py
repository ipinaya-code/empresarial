"""
Servicio de Reservas — Lógica de negocio transaccional.

Implementa los tres flujos de reserva:
1. Inseguro (sin bloqueo) — para demostrar la condición de carrera
2. Seguro (SELECT FOR UPDATE) — bloqueo pesimista
3. Provisional — reserva temporal con TTL

Genera códigos PNR estilo aerolínea y maneja toda la lógica
de estados y expiración.
"""

import datetime
import random
import string
import time

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import (
    AsientoNoDisponibleError,
    AsientoNoEncontradoError,
    ReservaActivaDuplicadaError,
    ReservaExpiradaError,
    ReservaNoEncontradaError,
    ReservaNoModificableError,
    UsuarioNoEncontradoError,
)
from app.core.logging import get_logger
from app.db.cache import cache_delete, cache_flush
from app.models.asiento import Asiento, EstadoAsiento
from app.models.reserva import EstadoReserva, Reserva
from app.models.usuario import Usuario

logger = get_logger("reservas")
settings = get_settings()


def _generar_codigo_reserva() -> str:
    """Genera un código PNR único estilo aerolínea."""
    chars = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"BOA-{chars}"


def _invalidar_cache_vuelo(asiento: Asiento) -> None:
    """Invalida la caché de disponibilidad del vuelo asociado al asiento."""
    cache_delete(f"vuelo:{asiento.vuelo_id}:disponibilidad")


def _validar_usuario(db: Session, usuario_id: int) -> Usuario:
    """Valida que el usuario exista."""
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise UsuarioNoEncontradoError(usuario_id)
    return usuario


# ════════════════════════════════════════════════════════════════
#  FLUJO INSEGURO — Sin bloqueo (demuestra Race Condition)
# ════════════════════════════════════════════════════════════════

def reservar_inseguro(db: Session, usuario_id: int, asiento_id: int) -> Reserva:
    """
    Flujo SIN control de concurrencia.

    Este endpoint existe SOLO para demostrar qué sucede cuando no se
    usa SELECT FOR UPDATE. Permite que múltiples solicitudes simultáneas
    lean el asiento como 'disponible' antes de que alguna lo confirme.
    """
    asiento = db.query(Asiento).filter(Asiento.id == asiento_id).first()
    if not asiento:
        raise AsientoNoEncontradoError(asiento_id)

    _validar_usuario(db, usuario_id)

    if asiento.estado != EstadoAsiento.DISPONIBLE:
        raise AsientoNoDisponibleError(asiento_id)

    # Simular latencia de procesamiento (ventana de race condition)
    time.sleep(settings.insecure_delay_seconds)

    asiento.estado = EstadoAsiento.CONFIRMADO
    nueva_reserva = Reserva(
        codigo_reserva=_generar_codigo_reserva(),
        usuario_id=usuario_id,
        asiento_id=asiento_id,
        estado=EstadoReserva.CONFIRMADA,
    )
    db.add(nueva_reserva)

    try:
        db.commit()
        db.refresh(nueva_reserva)
        _invalidar_cache_vuelo(asiento)
        logger.info(f"[INSEGURO] Reserva {nueva_reserva.codigo_reserva} creada — Usuario {usuario_id}, Asiento {asiento_id}")
        return nueva_reserva
    except IntegrityError:
        db.rollback()
        raise ReservaActivaDuplicadaError()


# ════════════════════════════════════════════════════════════════
#  FLUJO SEGURO — SELECT FOR UPDATE (Bloqueo Pesimista)
# ════════════════════════════════════════════════════════════════

def reservar_seguro(db: Session, usuario_id: int, asiento_id: int) -> Reserva:
    """
    Flujo CON control de concurrencia usando bloqueo pesimista.

    1. SELECT ... FOR UPDATE bloquea la fila del asiento.
    2. Simula un procesamiento largo (60s) manteniendo el bloqueo.
    3. Solo UNA solicitud puede confirmar; las demás esperan y fallan.
    """
    try:
        # Bloqueo pesimista: la fila queda bloqueada hasta COMMIT/ROLLBACK
        asiento = (
            db.query(Asiento)
            .filter(Asiento.id == asiento_id)
            .with_for_update()
            .first()
        )

        if not asiento:
            raise AsientoNoEncontradoError(asiento_id)

        _validar_usuario(db, usuario_id)

        if asiento.estado != EstadoAsiento.DISPONIBLE:
            db.rollback()
            raise AsientoNoDisponibleError(asiento_id)

        # Simular procesamiento largo mientras el bloqueo está activo
        logger.info(
            f"[SEGURO] Bloqueo adquirido para asiento {asiento_id} "
            f"— simulando procesamiento de {settings.secure_lock_delay_seconds}s"
        )
        time.sleep(settings.secure_lock_delay_seconds)

        asiento.estado = EstadoAsiento.CONFIRMADO
        nueva_reserva = Reserva(
            codigo_reserva=_generar_codigo_reserva(),
            usuario_id=usuario_id,
            asiento_id=asiento_id,
            estado=EstadoReserva.CONFIRMADA,
        )
        db.add(nueva_reserva)
        db.commit()
        db.refresh(nueva_reserva)

        _invalidar_cache_vuelo(asiento)
        logger.info(f"[SEGURO] Reserva {nueva_reserva.codigo_reserva} confirmada — Usuario {usuario_id}, Asiento {asiento_id}")
        return nueva_reserva

    except (AsientoNoEncontradoError, UsuarioNoEncontradoError, AsientoNoDisponibleError):
        db.rollback()
        raise
    except IntegrityError:
        db.rollback()
        raise ReservaActivaDuplicadaError()
    except Exception as e:
        db.rollback()
        logger.exception(f"Error inesperado al reservar asiento {asiento_id}")
        raise


# ════════════════════════════════════════════════════════════════
#  FLUJO PROVISIONAL — Reserva temporal con TTL
# ════════════════════════════════════════════════════════════════

def reservar_provisional(db: Session, usuario_id: int, asiento_id: int) -> Reserva:
    """
    Crea una reserva provisional (PENDIENTE) con TTL de 10 minutos.

    El asiento pasa a RESERVADO_PROVISIONAL y el pasajero tiene
    10 minutos para confirmar antes de que expire automáticamente.
    Inspirado en IATA NDC Offer Validity Windows.
    """
    try:
        asiento = (
            db.query(Asiento)
            .filter(Asiento.id == asiento_id)
            .with_for_update()
            .first()
        )
        if not asiento:
            raise AsientoNoEncontradoError(asiento_id)

        _validar_usuario(db, usuario_id)

        if asiento.estado != EstadoAsiento.DISPONIBLE:
            raise AsientoNoDisponibleError(asiento_id)

        expiracion = datetime.datetime.utcnow() + datetime.timedelta(
            minutes=settings.provisional_ttl_minutes
        )

        asiento.estado = EstadoAsiento.RESERVADO_PROVISIONAL
        asiento.fecha_expiracion = expiracion

        nueva_reserva = Reserva(
            codigo_reserva=_generar_codigo_reserva(),
            usuario_id=usuario_id,
            asiento_id=asiento_id,
            estado=EstadoReserva.PENDIENTE,
            fecha_expiracion=expiracion,
        )
        db.add(nueva_reserva)
        db.commit()
        db.refresh(nueva_reserva)

        _invalidar_cache_vuelo(asiento)
        logger.info(
            f"[PROVISIONAL] Reserva {nueva_reserva.codigo_reserva} creada "
            f"— Usuario {usuario_id}, Asiento {asiento_id}, expira {expiracion}"
        )
        return nueva_reserva

    except (AsientoNoEncontradoError, UsuarioNoEncontradoError, AsientoNoDisponibleError):
        db.rollback()
        raise
    except IntegrityError:
        db.rollback()
        raise ReservaActivaDuplicadaError()
    except Exception:
        db.rollback()
        logger.exception(f"Error al crear reserva provisional para asiento {asiento_id}")
        raise


# ════════════════════════════════════════════════════════════════
#  CONFIRMAR y EXPIRAR reservas provisionales
# ════════════════════════════════════════════════════════════════

def confirmar_reserva(db: Session, reserva_id: int) -> Reserva:
    """
    Confirma una reserva provisional vigente.

    Si la reserva ha expirado, la cancela automáticamente y libera el asiento.
    """
    reserva = (
        db.query(Reserva)
        .filter(Reserva.id == reserva_id)
        .with_for_update()
        .first()
    )
    if not reserva:
        raise ReservaNoEncontradaError(reserva_id)

    if reserva.estado != EstadoReserva.PENDIENTE:
        raise ReservaNoModificableError(reserva_id)

    asiento = (
        db.query(Asiento)
        .filter(Asiento.id == reserva.asiento_id)
        .with_for_update()
        .first()
    )

    # Verificar expiración
    if reserva.fecha_expiracion and reserva.fecha_expiracion <= datetime.datetime.utcnow():
        reserva.estado = EstadoReserva.CANCELADA
        asiento.estado = EstadoAsiento.DISPONIBLE
        asiento.fecha_expiracion = None
        db.commit()
        logger.warning(f"Reserva {reserva.codigo_reserva} expirada al intentar confirmar")
        raise ReservaExpiradaError(reserva_id)

    reserva.estado = EstadoReserva.CONFIRMADA
    asiento.estado = EstadoAsiento.CONFIRMADO
    asiento.fecha_expiracion = None
    db.commit()
    db.refresh(reserva)

    _invalidar_cache_vuelo(asiento)
    logger.info(f"Reserva {reserva.codigo_reserva} confirmada exitosamente")
    return reserva


def expirar_reservas(db: Session) -> dict:
    """
    Cancela todas las reservas provisionales vencidas y libera los asientos.

    En producción, esto sería ejecutado por un cron job o un worker en segundo plano.
    """
    ahora = datetime.datetime.utcnow()
    pendientes = (
        db.query(Reserva)
        .filter(
            Reserva.estado == EstadoReserva.PENDIENTE,
            Reserva.fecha_expiracion <= ahora,
        )
        .with_for_update()
        .all()
    )

    codigos_expirados = []
    for reserva in pendientes:
        asiento = (
            db.query(Asiento)
            .filter(Asiento.id == reserva.asiento_id)
            .with_for_update()
            .first()
        )
        reserva.estado = EstadoReserva.CANCELADA
        if asiento and asiento.estado == EstadoAsiento.RESERVADO_PROVISIONAL:
            asiento.estado = EstadoAsiento.DISPONIBLE
            asiento.fecha_expiracion = None
        codigos_expirados.append(reserva.codigo_reserva)

    db.commit()
    if pendientes:
        cache_flush()
        logger.info(f"Reservas expiradas: {codigos_expirados}")

    return {
        "msg": f"{len(pendientes)} reservas provisionales expiradas",
        "expiradas": len(pendientes),
        "codigos": codigos_expirados,
    }

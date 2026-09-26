"""
Excepciones de dominio del sistema de reservas BoA.

Estas excepciones se lanzan desde la capa de servicios y se traducen
a respuestas HTTP en la capa de API. Esto desacopla la lógica de negocio
del framework web.
"""

from fastapi import HTTPException, status


class BoABaseException(Exception):
    """Excepción base del dominio BoA."""

    def __init__(self, detail: str, status_code: int = 500):
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)


class AsientoNoEncontradoError(BoABaseException):
    """El asiento solicitado no existe en la base de datos."""

    def __init__(self, asiento_id: int):
        super().__init__(
            detail=f"Asiento con ID {asiento_id} no encontrado",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class UsuarioNoEncontradoError(BoABaseException):
    """El usuario solicitado no existe en la base de datos."""

    def __init__(self, usuario_id: int):
        super().__init__(
            detail=f"Usuario con ID {usuario_id} no encontrado",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class VueloNoEncontradoError(BoABaseException):
    """El vuelo solicitado no existe en la base de datos."""

    def __init__(self, vuelo_id: int):
        super().__init__(
            detail=f"Vuelo con ID {vuelo_id} no encontrado",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class ReservaNoEncontradaError(BoABaseException):
    """La reserva solicitada no existe en la base de datos."""

    def __init__(self, reserva_id: int):
        super().__init__(
            detail=f"Reserva con ID {reserva_id} no encontrada",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class AsientoNoDisponibleError(BoABaseException):
    """El asiento solicitado ya no está disponible para reserva."""

    def __init__(self, asiento_id: int | None = None):
        detail = "El asiento solicitado no está disponible"
        if asiento_id:
            detail = f"Asiento {asiento_id} no está disponible"
        super().__init__(detail=detail, status_code=status.HTTP_409_CONFLICT)


class ReservaActivaDuplicadaError(BoABaseException):
    """Ya existe una reserva activa para este asiento."""

    def __init__(self):
        super().__init__(
            detail="El asiento ya tiene una reserva activa (PENDIENTE o CONFIRMADA)",
            status_code=status.HTTP_409_CONFLICT,
        )


class ReservaNoModificableError(BoABaseException):
    """La reserva ya no puede ser modificada (no está en estado PENDIENTE)."""

    def __init__(self, reserva_id: int):
        super().__init__(
            detail=f"La reserva {reserva_id} ya no está en estado pendiente",
            status_code=status.HTTP_409_CONFLICT,
        )


class ReservaExpiradaError(BoABaseException):
    """La reserva provisional ha expirado."""

    def __init__(self, reserva_id: int):
        super().__init__(
            detail=f"La reserva provisional {reserva_id} ha expirado",
            status_code=status.HTTP_409_CONFLICT,
        )


class DatosYaInicializadosError(BoABaseException):
    """Los datos semilla ya fueron cargados previamente."""

    def __init__(self):
        super().__init__(
            detail="Los datos de demostración ya están inicializados",
            status_code=status.HTTP_409_CONFLICT,
        )


def boa_exception_to_http(exc: BoABaseException) -> HTTPException:
    """Convierte una excepción de dominio a una respuesta HTTP de FastAPI."""
    return HTTPException(status_code=exc.status_code, detail=exc.detail)

"""
Modelo: Reserva.

Representa la relación entre un pasajero y un asiento en un vuelo de BoA.
Implementa la lógica de estados transaccionales con restricción de unicidad
parcial para prevenir sobreasignaciones.
"""

import datetime
import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Index, Integer, String, text
from sqlalchemy.orm import relationship

from app.db.session import Base


class EstadoReserva(enum.Enum):
    """Estados del ciclo de vida de una reserva."""

    PENDIENTE = "pendiente"          # Reserva provisional, esperando confirmación
    CONFIRMADA = "confirmada"        # Reserva confirmada y asiento asignado
    CANCELADA = "cancelada"          # Reserva cancelada (manual o por expiración)


class Reserva(Base):
    """Reserva de un pasajero para un asiento específico en un vuelo."""

    __tablename__ = "reservas"

    id = Column(Integer, primary_key=True, index=True)
    codigo_reserva = Column(
        String(10),
        unique=True,
        nullable=False,
        index=True,
        comment="Código PNR de la reserva (ej: BOA-A1B2C3)",
    )
    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    asiento_id = Column(
        Integer,
        ForeignKey("asientos.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    fecha_reserva = Column(
        DateTime,
        nullable=False,
        default=datetime.datetime.utcnow,
        comment="Fecha y hora de creación de la reserva",
    )
    fecha_expiracion = Column(
        DateTime,
        nullable=True,
        comment="Fecha límite para confirmar una reserva provisional",
    )
    estado = Column(
        Enum(EstadoReserva),
        nullable=False,
        default=EstadoReserva.PENDIENTE,
        index=True,
    )

    # Relaciones
    usuario = relationship("Usuario", back_populates="reservas")
    asiento = relationship("Asiento", back_populates="reservas")

    def __repr__(self) -> str:
        return (
            f"<Reserva(id={self.id}, codigo='{self.codigo_reserva}', "
            f"usuario_id={self.usuario_id}, asiento_id={self.asiento_id}, "
            f"estado={self.estado.value})>"
        )


# Índice único parcial: impide más de una reserva activa por asiento.
# Solo aplica a reservas en estado PENDIENTE o CONFIRMADA.
# Las reservas CANCELADAS quedan como historial.
Index(
    "uq_reserva_asiento_activa",
    Reserva.asiento_id,
    unique=True,
    postgresql_where=text("estado IN ('pendiente', 'confirmada')"),
)

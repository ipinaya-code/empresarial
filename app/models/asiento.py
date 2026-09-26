"""
Modelo: Asiento.

Representa un asiento específico dentro de un vuelo de BoA.
Incluye clase de servicio (ejecutiva/económica) y manejo de estados
para el control de concurrencia.
"""

import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.session import Base


class EstadoAsiento(enum.Enum):
    """Estados posibles de un asiento."""

    DISPONIBLE = "disponible"
    RESERVADO_PROVISIONAL = "reservado_provisional"
    CONFIRMADO = "confirmado"
    BLOQUEADO = "bloqueado"  # Mantenimiento o reserva VIP


class ClaseServicio(enum.Enum):
    """Clases de servicio según la aeronave."""

    EJECUTIVA = "ejecutiva"
    ECONOMICA = "economica"


class Asiento(Base):
    """Asiento individual perteneciente a un vuelo de BoA."""

    __tablename__ = "asientos"

    id = Column(Integer, primary_key=True, index=True)
    vuelo_id = Column(
        Integer,
        ForeignKey("vuelos.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    numero = Column(
        String(5),
        nullable=False,
        index=True,
        comment="Identificador del asiento (ej: 1A, 14F)",
    )
    fila = Column(Integer, nullable=False, comment="Número de fila (1-22)")
    columna = Column(String(1), nullable=False, comment="Letra de columna (A-F)")
    clase = Column(
        Enum(ClaseServicio),
        nullable=False,
        default=ClaseServicio.ECONOMICA,
        comment="Clase de servicio: ejecutiva o económica",
    )
    estado = Column(
        Enum(EstadoAsiento),
        nullable=False,
        default=EstadoAsiento.DISPONIBLE,
        index=True,
    )
    fecha_expiracion = Column(
        DateTime,
        nullable=True,
        comment="Límite de reserva provisional (NULL si no aplica)",
    )

    # Relaciones
    vuelo = relationship("Vuelo", back_populates="asientos")
    reservas = relationship("Reserva", back_populates="asiento", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Asiento(id={self.id}, numero='{self.numero}', clase={self.clase.value}, estado={self.estado.value})>"

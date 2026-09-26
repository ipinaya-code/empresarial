"""
Modelo: Vuelo.

Representa un vuelo comercial de BoA con datos realistas.
Utiliza códigos IATA para aeropuertos y el prefijo OB de BoA.
"""

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.db.session import Base


class Vuelo(Base):
    """Vuelo comercial de Boliviana de Aviación."""

    __tablename__ = "vuelos"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(
        String(10),
        unique=True,
        nullable=False,
        index=True,
        comment="Código de vuelo IATA (ej: OB-101)",
    )
    origen_iata = Column(
        String(3),
        nullable=False,
        index=True,
        comment="Código IATA del aeropuerto de origen (ej: VVI)",
    )
    origen_nombre = Column(
        String(100),
        nullable=False,
        comment="Nombre completo del aeropuerto de origen",
    )
    destino_iata = Column(
        String(3),
        nullable=False,
        index=True,
        comment="Código IATA del aeropuerto de destino (ej: LPB)",
    )
    destino_nombre = Column(
        String(100),
        nullable=False,
        comment="Nombre completo del aeropuerto de destino",
    )
    fecha_salida = Column(DateTime, nullable=False, index=True, comment="Fecha y hora de salida programada")
    fecha_llegada = Column(DateTime, nullable=False, comment="Fecha y hora de llegada estimada")
    aeronave = Column(
        String(50),
        nullable=False,
        default="Boeing 737-300",
        comment="Tipo de aeronave asignada",
    )
    capacidad = Column(Integer, nullable=False, comment="Capacidad total de asientos")
    estado = Column(
        String(20),
        nullable=False,
        default="PROGRAMADO",
        index=True,
        comment="Estado: PROGRAMADO, ABORDANDO, EN_VUELO, ATERRIZADO, CANCELADO",
    )

    # Relaciones
    asientos = relationship("Asiento", back_populates="vuelo", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Vuelo(id={self.id}, codigo='{self.codigo}', {self.origen_iata}→{self.destino_iata})>"

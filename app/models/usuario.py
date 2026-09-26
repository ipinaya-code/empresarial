"""
Modelo: Usuario (Pasajero).

Representa a un pasajero registrado en el sistema de reservas de BoA.
Basado en los estándares IATA para datos de pasajero (nombre, documento, contacto).
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.session import Base


class Usuario(Base):
    """Pasajero que puede realizar reservas de vuelos."""

    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, index=True, comment="Nombre completo del pasajero")
    apellido = Column(String(100), nullable=False, index=True, comment="Apellido del pasajero")
    email = Column(String(255), unique=True, nullable=False, index=True, comment="Correo electrónico único")
    documento_tipo = Column(
        String(20),
        nullable=False,
        default="CI",
        comment="Tipo de documento: CI, PASAPORTE, DNI",
    )
    documento_numero = Column(
        String(20),
        nullable=False,
        unique=True,
        index=True,
        comment="Número de documento de identidad",
    )
    telefono = Column(String(20), nullable=True, comment="Teléfono de contacto")
    nacionalidad = Column(String(3), nullable=False, default="BOL", comment="Código ISO 3166-1 alpha-3")

    # Relaciones
    reservas = relationship("Reserva", back_populates="usuario", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Usuario(id={self.id}, nombre='{self.nombre} {self.apellido}', email='{self.email}')>"

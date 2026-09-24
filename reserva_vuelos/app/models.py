from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
import enum
import datetime
from app.database import Base

class EstadoAsiento(enum.Enum):
    DISPONIBLE = "disponible"
    RESERVADO_PROVISIONAL = "reservado_provisional"
    CONFIRMADO = "confirmado"

class EstadoReserva(enum.Enum):
    PENDIENTE = "pendiente"
    CONFIRMADA = "confirmada"
    CANCELADA = "cancelada"

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    email = Column(String, unique=True, index=True)

class Vuelo(Base):
    __tablename__ = "vuelos"
    id = Column(Integer, primary_key=True, index=True)
    origen = Column(String, index=True)
    destino = Column(String, index=True)
    fecha = Column(DateTime)
    capacidad = Column(Integer)
    asientos = relationship("Asiento", back_populates="vuelo")

class Asiento(Base):
    __tablename__ = "asientos"
    id = Column(Integer, primary_key=True, index=True)
    vuelo_id = Column(Integer, ForeignKey("vuelos.id"))
    numero = Column(String, index=True)
    estado = Column(Enum(EstadoAsiento), default=EstadoAsiento.DISPONIBLE)
    vuelo = relationship("Vuelo", back_populates="asientos")

class Reserva(Base):
    __tablename__ = "reservas"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    asiento_id = Column(Integer, ForeignKey("asientos.id"))
    fecha_reserva = Column(DateTime, default=datetime.datetime.utcnow)
    estado = Column(Enum(EstadoReserva), default=EstadoReserva.PENDIENTE)

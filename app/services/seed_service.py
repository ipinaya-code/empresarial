"""
Servicio de Seed — Datos de demostración realistas de BoA.

Genera vuelos, asientos y pasajeros simulados basados en la operación
real de Boliviana de Aviación:
- Rutas domésticas reales (VVI↔LPB, VVI↔CBB, etc.)
- Aeropuertos con códigos IATA correctos
- Configuración de asientos Boeing 737-300 (ejecutiva + económica)
- Horarios realistas
- Pasajeros con nombres y documentos bolivianos simulados
"""

import datetime
import random
import string

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.cache import cache_flush
from app.models.asiento import Asiento, ClaseServicio, EstadoAsiento
from app.models.reserva import Reserva
from app.models.usuario import Usuario
from app.models.vuelo import Vuelo

logger = get_logger("seed")

# ── Aeropuertos de Bolivia (datos reales IATA) ──────────────────
AEROPUERTOS = {
    "VVI": "Aeropuerto Internacional Viru Viru — Santa Cruz",
    "LPB": "Aeropuerto Internacional El Alto — La Paz",
    "CBB": "Aeropuerto Jorge Wilstermann — Cochabamba",
    "SRE": "Aeropuerto Alcantarí — Sucre",
    "TJA": "Aeropuerto Capitán Oriel Lea Plaza — Tarija",
    "ORU": "Aeropuerto Juan Mendoza — Oruru",
    "TDD": "Aeropuerto Teniente Jorge Henrich Arauz — Trinidad",
    "CIJ": "Aeropuerto Capitán Aníbal Arab — Cobija",
    "SRZ": "Aeropuerto El Trompillo — Santa Cruz (doméstico)",
}

# ── Rutas domésticas de BoA (basadas en operación real) ──────────
RUTAS = [
    ("VVI", "LPB", 55),  # Santa Cruz → La Paz (55 min)
    ("LPB", "VVI", 55),  # La Paz → Santa Cruz
    ("VVI", "CBB", 40),  # Santa Cruz → Cochabamba
    ("CBB", "VVI", 40),  # Cochabamba → Santa Cruz
    ("LPB", "CBB", 35),  # La Paz → Cochabamba
    ("CBB", "LPB", 35),  # Cochabamba → La Paz
    ("VVI", "SRE", 45),  # Santa Cruz → Sucre
    ("VVI", "TJA", 50),  # Santa Cruz → Tarija
    ("LPB", "ORU", 30),  # La Paz → Oruro
    ("VVI", "TDD", 45),  # Santa Cruz → Trinidad
    ("VVI", "CIJ", 90),  # Santa Cruz → Cobija
    ("LPB", "SRE", 40),  # La Paz → Sucre
]

# ── Horarios de salida realistas ──────────────────────────────────
HORARIOS = [
    (6, 0),  # 06:00 — Primer vuelo
    (8, 30),  # 08:30 — Mañana
    (12, 0),  # 12:00 — Mediodía
    (15, 30),  # 15:30 — Tarde
    (19, 0),  # 19:00 — Noche
]

# ── Pasajeros bolivianos simulados ────────────────────────────────
NOMBRES_BOLIVIANOS = [
    ("Carlos", "Mamani"),
    ("María", "Quispe"),
    ("Juan", "Condori"),
    ("Ana", "Choque"),
    ("Pedro", "Flores"),
    ("Lucía", "Huanca"),
    ("Roberto", "Alanoca"),
    ("Sofía", "Poma"),
    ("Diego", "Gutiérrez"),
    ("Valentina", "Morales"),
    ("Andrés", "Ticona"),
    ("Camila", "Apaza"),
    ("Fernando", "Callisaya"),
    ("Isabella", "Limachi"),
    ("Gabriel", "Copa"),
    ("Daniela", "Colque"),
    ("Mateo", "Yujra"),
    ("Paula", "Nina"),
    ("Sebastián", "Tarqui"),
    ("Mariana", "Machaca"),
]

# ── Configuración Boeing 737-300 ──────────────────────────────────
COLUMNAS_737 = ["A", "B", "C", "D", "E", "F"]  # 6 asientos por fila (3-3)
FILAS_EJECUTIVA = range(1, 4)  # Filas 1-3 (18 asientos ejecutiva)
FILAS_ECONOMICA = range(4, 23)  # Filas 4-22 (114 asientos económica)
CAPACIDAD_TOTAL_737 = len(FILAS_EJECUTIVA) * len(COLUMNAS_737) + len(FILAS_ECONOMICA) * len(COLUMNAS_737)


def _generar_codigo_vuelo(indice: int) -> str:
    """Genera un código de vuelo con prefijo OB (IATA de BoA)."""
    return f"OB-{100 + indice}"


def _generar_documento() -> str:
    """Genera un número de CI boliviano simulado."""
    return str(random.randint(1_000_000, 15_000_000))


def _generar_codigo_reserva() -> str:
    """Genera un código PNR estilo aerolínea (ej: BOA-A1B2C3)."""
    chars = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"BOA-{chars}"


def crear_datos_semilla(db: Session) -> dict:
    """
    Crea datos de demostración realistas de BoA.

    Genera:
    - 12 rutas domésticas con horarios variados
    - Asientos con configuración Boeing 737-300 (ejecutiva + económica)
    - 20 pasajeros con nombres bolivianos
    """
    # Verificar si ya existen datos
    vuelo_existente = db.query(Vuelo).first()
    if vuelo_existente:
        asiento = db.query(Asiento).first()
        usuario = db.query(Usuario).first()
        return {
            "msg": "Los datos de demostración ya están inicializados",
            "vuelos": db.query(Vuelo).count(),
            "asientos": db.query(Asiento).count(),
            "usuarios": db.query(Usuario).count(),
            "primer_vuelo_id": vuelo_existente.id,
            "primer_asiento_id": asiento.id if asiento else None,
            "primer_usuario_id": usuario.id if usuario else None,
        }

    logger.info("Inicializando datos de demostración de BoA...")

    # ── 1. Crear vuelos con rutas reales ────────────────────────
    fecha_base = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    fecha_base += datetime.timedelta(days=1)  # Vuelos del día siguiente

    vuelos_creados = []
    indice_vuelo = 0

    for origen_iata, destino_iata, duracion_min in RUTAS:
        # Un vuelo por ruta (primer horario disponible)
        hora, minuto = HORARIOS[indice_vuelo % len(HORARIOS)]
        fecha_salida = fecha_base.replace(hour=hora, minute=minuto)
        fecha_llegada = fecha_salida + datetime.timedelta(minutes=duracion_min)

        vuelo = Vuelo(
            codigo=_generar_codigo_vuelo(indice_vuelo),
            origen_iata=origen_iata,
            origen_nombre=AEROPUERTOS[origen_iata],
            destino_iata=destino_iata,
            destino_nombre=AEROPUERTOS[destino_iata],
            fecha_salida=fecha_salida,
            fecha_llegada=fecha_llegada,
            aeronave="Boeing 737-300",
            capacidad=CAPACIDAD_TOTAL_737,
            estado="PROGRAMADO",
        )
        db.add(vuelo)
        db.flush()  # Para obtener el ID

        # ── 2. Crear asientos con configuración real del 737-300 ──
        asientos = []
        for fila in FILAS_EJECUTIVA:
            for col in COLUMNAS_737:
                asientos.append(
                    Asiento(
                        vuelo_id=vuelo.id,
                        numero=f"{fila}{col}",
                        fila=fila,
                        columna=col,
                        clase=ClaseServicio.EJECUTIVA,
                        estado=EstadoAsiento.DISPONIBLE,
                    )
                )
        for fila in FILAS_ECONOMICA:
            for col in COLUMNAS_737:
                asientos.append(
                    Asiento(
                        vuelo_id=vuelo.id,
                        numero=f"{fila}{col}",
                        fila=fila,
                        columna=col,
                        clase=ClaseServicio.ECONOMICA,
                        estado=EstadoAsiento.DISPONIBLE,
                    )
                )
        db.add_all(asientos)
        vuelos_creados.append(vuelo)
        indice_vuelo += 1

    # ── 3. Crear pasajeros con datos bolivianos ─────────────────
    documentos_usados = set()
    for i, (nombre, apellido) in enumerate(NOMBRES_BOLIVIANOS):
        doc = _generar_documento()
        while doc in documentos_usados:
            doc = _generar_documento()
        documentos_usados.add(doc)

        usuario = Usuario(
            nombre=nombre,
            apellido=apellido,
            email=f"{nombre.lower()}.{apellido.lower()}@correo.bo",
            documento_tipo="CI",
            documento_numero=doc,
            telefono=f"+591 7{random.randint(0, 9)}{random.randint(100000, 999999)}",
            nacionalidad="BOL",
        )
        db.add(usuario)

    db.commit()

    primer_vuelo = vuelos_creados[0]
    primer_asiento = db.query(Asiento).filter(Asiento.vuelo_id == primer_vuelo.id).first()
    primer_usuario = db.query(Usuario).first()

    cache_flush()

    resultado = {
        "msg": "Datos de demostración de BoA inicializados correctamente",
        "vuelos_creados": len(vuelos_creados),
        "asientos_por_vuelo": CAPACIDAD_TOTAL_737,
        "total_asientos": len(vuelos_creados) * CAPACIDAD_TOTAL_737,
        "pasajeros_creados": len(NOMBRES_BOLIVIANOS),
        "rutas": [f"{o}→{d}" for o, d, _ in RUTAS],
        "primer_vuelo_id": primer_vuelo.id,
        "primer_asiento_id": primer_asiento.id if primer_asiento else None,
        "primer_usuario_id": primer_usuario.id if primer_usuario else None,
    }
    logger.info(f"Seed completado: {resultado}")
    return resultado


def resetear_datos(db: Session) -> dict:
    """
    Elimina reservas y libera todos los asientos para repetir pruebas.
    No elimina vuelos ni usuarios.
    """
    reservas_eliminadas = db.query(Reserva).delete(synchronize_session=False)
    asientos_actualizados = db.query(Asiento).update(
        {"estado": EstadoAsiento.DISPONIBLE, "fecha_expiracion": None},
        synchronize_session=False,
    )
    db.commit()
    cache_flush()

    logger.info(f"Reset: {reservas_eliminadas} reservas eliminadas, {asientos_actualizados} asientos liberados")
    return {
        "msg": "Datos reseteados correctamente",
        "reservas_eliminadas": reservas_eliminadas,
        "asientos_liberados": asientos_actualizados,
    }

"""
Servicio de Disponibilidad — CQRS (Query Side).

Implementa el lado de lectura del patrón CQRS.
Las consultas de disponibilidad son las operaciones de mayor tráfico
y no necesitan bloqueos. Se cachean en Valkey para reducir la carga
en PostgreSQL.
"""

from sqlalchemy.orm import Session

from app.core.exceptions import VueloNoEncontradoError
from app.core.logging import get_logger
from app.db.cache import cache_get, cache_set
from app.models.asiento import Asiento, ClaseServicio, EstadoAsiento
from app.models.vuelo import Vuelo

logger = get_logger("disponibilidad")


def consultar_disponibilidad(db: Session, vuelo_id: int) -> dict:
    """
    Consulta la disponibilidad de asientos de un vuelo (CQRS: Query).

    1. Intenta leer de la caché Valkey (Cache Hit).
    2. Si no existe, consulta PostgreSQL sin bloqueos.
    3. Almacena el resultado en caché con TTL configurable.

    En producción, esta consulta podría dirigirse a una réplica
    de lectura de PostgreSQL para descargar al maestro.
    """
    cache_key = f"vuelo:{vuelo_id}:disponibilidad"

    # ── 1. Intentar Cache Hit ──────────────────────────────────
    cached = cache_get(cache_key)
    if cached:
        logger.info(f"Cache HIT para vuelo {vuelo_id}")
        return cached

    logger.info(f"Cache MISS para vuelo {vuelo_id} — consultando PostgreSQL")

    # ── 2. Consultar PostgreSQL (sin bloqueos) ─────────────────
    vuelo = db.query(Vuelo).filter(Vuelo.id == vuelo_id).first()
    if not vuelo:
        raise VueloNoEncontradoError(vuelo_id)

    asientos = db.query(Asiento).filter(Asiento.vuelo_id == vuelo_id).all()

    # ── 3. Calcular disponibilidad por clase ───────────────────
    disponibles_ejecutiva = sum(
        1 for a in asientos if a.estado == EstadoAsiento.DISPONIBLE and a.clase == ClaseServicio.EJECUTIVA
    )
    disponibles_economica = sum(
        1 for a in asientos if a.estado == EstadoAsiento.DISPONIBLE and a.clase == ClaseServicio.ECONOMICA
    )
    total_disponibles = disponibles_ejecutiva + disponibles_economica

    response_data = {
        "vuelo_id": vuelo.id,
        "codigo": vuelo.codigo,
        "origen_iata": vuelo.origen_iata,
        "origen_nombre": vuelo.origen_nombre,
        "destino_iata": vuelo.destino_iata,
        "destino_nombre": vuelo.destino_nombre,
        "aeronave": vuelo.aeronave,
        "fecha_salida": vuelo.fecha_salida.isoformat(),
        "capacidad_total": vuelo.capacidad,
        "asientos_disponibles": total_disponibles,
        "asientos_ejecutiva_disponibles": disponibles_ejecutiva,
        "asientos_economica_disponibles": disponibles_economica,
        "asientos": [
            {
                "id": a.id,
                "numero": a.numero,
                "fila": a.fila,
                "columna": a.columna,
                "clase": a.clase.value,
                "estado": a.estado.value,
            }
            for a in asientos
        ],
    }

    # ── 4. Cachear resultado ───────────────────────────────────
    cache_set(cache_key, response_data)

    return response_data

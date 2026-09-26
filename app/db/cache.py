"""
Cliente de caché Valkey/Redis.

Provee un singleton del cliente Valkey con manejo seguro de errores.
Si Valkey no está disponible, la aplicación sigue funcionando sin caché
(graceful degradation).
"""

import json
import logging
from typing import Any

import redis

from app.core.config import get_settings

logger = logging.getLogger("boa.cache")

settings = get_settings()

try:
    valkey_client: redis.Redis | None = redis.from_url(
        settings.valkey_url,
        decode_responses=True,
        socket_connect_timeout=3,
        socket_timeout=3,
        retry_on_timeout=True,
    )
    # Test de conexión al inicio
    valkey_client.ping()
    logger.info("Conexión a Valkey establecida correctamente")
except Exception as e:
    logger.warning(f"Valkey no disponible, la aplicación operará sin caché: {e}")
    valkey_client = None


def get_valkey() -> redis.Redis | None:
    """Retorna el cliente Valkey o None si no está disponible."""
    return valkey_client


def cache_get(key: str) -> dict | None:
    """Lee un valor del caché. Retorna None si no existe o si hay error."""
    client = get_valkey()
    if not client:
        return None
    try:
        data = client.get(key)
        if data:
            logger.debug(f"Cache HIT: {key}")
            return json.loads(data)
        logger.debug(f"Cache MISS: {key}")
        return None
    except Exception as e:
        logger.error(f"Error leyendo caché [{key}]: {e}")
        return None


def cache_set(key: str, value: Any, ttl: int | None = None) -> bool:
    """Escribe un valor en el caché con TTL opcional."""
    client = get_valkey()
    if not client:
        return False
    try:
        ttl = ttl or settings.cache_ttl_seconds
        client.setex(key, ttl, json.dumps(value, default=str))
        logger.debug(f"Cache SET: {key} (TTL={ttl}s)")
        return True
    except Exception as e:
        logger.error(f"Error escribiendo caché [{key}]: {e}")
        return False


def cache_delete(key: str) -> bool:
    """Elimina una clave específica del caché."""
    client = get_valkey()
    if not client:
        return False
    try:
        client.delete(key)
        logger.debug(f"Cache DELETE: {key}")
        return True
    except Exception as e:
        logger.error(f"Error eliminando caché [{key}]: {e}")
        return False


def cache_flush() -> bool:
    """Limpia todo el caché. Usar con precaución."""
    client = get_valkey()
    if not client:
        return False
    try:
        client.flushdb()
        logger.info("Cache FLUSH: base de datos de caché limpiada")
        return True
    except Exception as e:
        logger.error(f"Error limpiando caché: {e}")
        return False

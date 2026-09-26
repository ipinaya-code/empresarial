"""
Router principal de la API v1.

Agrupa todos los sub-routers bajo el prefijo /api/v1.
"""

from fastapi import APIRouter

from app.api.v1.admin import router as admin_router
from app.api.v1.health import router as health_router
from app.api.v1.reservas import router as reservas_router
from app.api.v1.vuelos import router as vuelos_router

router = APIRouter()

router.include_router(health_router, tags=["🏥 Health"])
router.include_router(admin_router, prefix="/admin", tags=["🔧 Administración"])
router.include_router(vuelos_router, prefix="/vuelos", tags=["✈️ Vuelos (CQRS: Lectura)"])
router.include_router(reservas_router, prefix="/reservar", tags=["📋 Reservas (CQRS: Escritura)"])

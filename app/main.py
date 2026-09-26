"""
App Factory — Punto de entrada de la aplicación FastAPI.

Este módulo crea y configura la aplicación de forma limpia.
Es el único archivo que debe importarse para iniciar el servidor.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import router as v1_router
from app.core.config import get_settings
from app.core.exceptions import BoABaseException
from app.core.logging import setup_logging
from app.db.session import Base, engine

settings = get_settings()


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Ciclo de vida de la aplicación: startup y shutdown."""
    # ── Startup ───────────────────────────────────────────────
    setup_logging()
    # Crear tablas si no existen (en producción, usar Alembic)
    if not settings.is_production:
        try:
            Base.metadata.create_all(bind=engine)
        except Exception:
            pass  # BD no disponible, se creará al conectar (tests usan override)
    yield
    # ── Shutdown ──────────────────────────────────────────────
    engine.dispose()


def create_app() -> FastAPI:
    """Factory function que crea y configura la aplicación FastAPI."""
    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "Prototipo de sistema de reservas para Boliviana de Aviación (BoA).\n\n"
            "Demuestra el control de concurrencia transaccional al asignar asientos, "
            "utilizando bloqueo pesimista (SELECT FOR UPDATE), reservas provisionales "
            "con TTL, patrón CQRS con caché Valkey, y estándares IATA.\n\n"
            "**Arquitectura:** FastAPI + SQLAlchemy + PostgreSQL + Valkey\n\n"
            "**Equipo:** Iver Pinaya · Thiago Sossa · Nataly Crespo · Wilson Gonzales"
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
        openapi_tags=[
            {"name": "🏥 Health", "description": "Verificación del estado del servicio"},
            {"name": "🔧 Administración", "description": "Seed y reset de datos de demostración"},
            {"name": "✈️ Vuelos (CQRS: Lectura)", "description": "Consulta de disponibilidad (sin bloqueos)"},
            {"name": "📋 Reservas (CQRS: Escritura)", "description": "Reservas con control transaccional"},
        ],
    )

    # ── CORS ──────────────────────────────────────────────────
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Exception handler global ─────────────────────────────
    @application.exception_handler(BoABaseException)
    async def boa_exception_handler(request: Request, exc: BoABaseException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    # ── Routers ──────────────────────────────────────────────
    application.include_router(v1_router, prefix=settings.api_v1_prefix)

    # ── Retrocompatibilidad: montar endpoints en la raíz ─────
    # Para que los tests existentes sigan funcionando
    from app.api.v1.admin import router as admin_compat
    from app.api.v1.reservas import router as reservas_compat
    from app.api.v1.vuelos import router as vuelos_compat
    from app.api.v1.health import router as health_compat

    application.include_router(admin_compat, prefix="/admin", tags=["Retrocompatibilidad"], include_in_schema=False)
    application.include_router(reservas_compat, prefix="/reservar", tags=["Retrocompatibilidad"], include_in_schema=False)
    application.include_router(vuelos_compat, prefix="/vuelos", tags=["Retrocompatibilidad"], include_in_schema=False)
    application.include_router(health_compat, tags=["Retrocompatibilidad"], include_in_schema=False)

    return application


# Instancia de la aplicación — usada por uvicorn
app = create_app()

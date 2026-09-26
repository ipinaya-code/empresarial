"""
Endpoints de Health Check.

Endpoints para verificar el estado de la aplicación y sus dependencias.
Usados por Docker Compose, Kubernetes, y el CI/CD.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.cache import get_valkey

router = APIRouter()


@router.get("/health", summary="Health check básico")
def health():
    """Verifica que la API esté respondiendo."""
    return {"status": "ok", "service": "boa-reservas-api"}


@router.get("/health/ready", summary="Readiness check completo")
def readiness(db: Session = Depends(get_db)):
    """
    Verifica que la API y todas sus dependencias estén operativas.

    Comprueba:
    - PostgreSQL: ejecuta un SELECT 1
    - Valkey: ejecuta un PING
    """
    checks = {"api": "ok"}

    # PostgreSQL
    try:
        db.execute(text("SELECT 1"))
        checks["postgresql"] = "ok"
    except Exception as e:
        checks["postgresql"] = f"error: {e}"

    # Valkey
    valkey = get_valkey()
    if valkey:
        try:
            valkey.ping()
            checks["valkey"] = "ok"
        except Exception as e:
            checks["valkey"] = f"error: {e}"
    else:
        checks["valkey"] = "no disponible (degraded mode)"

    all_ok = all(v == "ok" for v in checks.values())
    return {
        "status": "ok" if all_ok else "degraded",
        "checks": checks,
    }

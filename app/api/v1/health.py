"""Liveness y readiness: PostgreSQL es obligatorio; Valkey es opcional."""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import get_settings
from app.db.cache import get_valkey

router = APIRouter()


@router.get("/health", summary="Liveness")
def health():
    return {"status": "ok", "service": "boa-reservas-api"}


@router.get("/health/ready", summary="Readiness")
def readiness(db: Session = Depends(get_db)):
    checks = {"postgresql": "ok", "valkey": "disabled"}
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        return JSONResponse(status_code=503, content={"status": "unavailable", "checks": {"postgresql": "error"}})
    if get_settings().cache_enabled:
        try:
            get_valkey().ping()
            checks["valkey"] = "ok"
        except Exception:
            checks["valkey"] = "unavailable"
    return {"status": "degraded" if checks["valkey"] == "unavailable" else "ok", "checks": checks}

"""
Módulo de compatibilidad con código legacy.

Redirige las importaciones antiguas a los nuevos módulos.
Permite que tests y scripts existentes sigan funcionando
mientras se migran a la nueva estructura.

DEPRECADO: Usar directamente los módulos nuevos:
    from app.db.session import Base, SessionLocal, engine, get_db
    from app.db.cache import get_valkey
"""

import warnings

warnings.warn(
    "app.database está deprecado. Usar app.db.session y app.db.cache",
    DeprecationWarning,
    stacklevel=2,
)

from app.db.session import Base, SessionLocal, engine, get_db  # noqa: F401, E402
from app.db.cache import get_valkey  # noqa: F401, E402

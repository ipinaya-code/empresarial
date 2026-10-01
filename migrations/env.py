"""Migraciones con la misma configuración que la aplicación."""

from alembic import context
from sqlalchemy import create_engine, pool

from app import models
from app.core.config import get_settings
from app.db.session import Base

if context.is_offline_mode():
    context.configure(url=get_settings().db_url, target_metadata=Base.metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()
else:
    engine = create_engine(get_settings().db_url, poolclass=pool.NullPool)
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=Base.metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()

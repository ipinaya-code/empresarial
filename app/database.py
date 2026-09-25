from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

import os

SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://admin:admin@localhost:5455/reservas_db",
)

if SQLALCHEMY_DATABASE_URL.startswith("postgresql://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace(
        "postgresql://", "postgresql+psycopg2://", 1
    )

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

import redis
VALKEY_URL = os.getenv("VALKEY_URL", "redis://localhost:6379/0")
try:
    # Utilizamos el cliente de redis-py, pero conectando a Valkey
    valkey_client = redis.from_url(VALKEY_URL, decode_responses=True)
except Exception:
    valkey_client = None

def get_valkey():
    return valkey_client

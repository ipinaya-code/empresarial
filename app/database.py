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
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
except Exception:
    redis_client = None

def get_redis():
    return redis_client

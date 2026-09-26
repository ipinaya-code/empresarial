# ─────────────────────────────────────────────────────────────
# Dockerfile — Sistema de Reservas BoA
# Multi-stage build para imagen optimizada
# ─────────────────────────────────────────────────────────────

# ── Stage 1: Builder ─────────────────────────────────────────
FROM docker.io/library/python:3.11-slim AS builder

WORKDIR /build

# Instalar dependencias del sistema para compilar psycopg2
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar solo los archivos de dependencias primero (cache de Docker)
COPY pyproject.toml ./
COPY requirements.txt ./

# Instalar dependencias de Python
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Stage 2: Runtime ────────────────────────────────────────
FROM docker.io/library/python:3.11-slim AS runtime

# Metadatos de la imagen
LABEL maintainer="Equipo BoA <ipinaya-code@github.com>"
LABEL description="API de Reservas de Vuelos — Boliviana de Aviación"
LABEL version="2.0.0"

WORKDIR /app

# Instalar solo las librerías runtime necesarias (no compiladores)
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r boa && useradd -r -g boa -d /app -s /sbin/nologin boa

# Copiar dependencias instaladas desde el builder
COPY --from=builder /install /usr/local

# Copiar código de la aplicación
COPY app/ ./app/
COPY .env.example ./.env.example

# Cambiar a usuario no-root
RUN chown -R boa:boa /app
USER boa

# Exponer puerto
EXPOSE 8000

# Health check del contenedor
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando de inicio
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]

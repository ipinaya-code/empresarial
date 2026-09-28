FROM docker.io/library/python:3.12-slim AS builder
WORKDIR /build
COPY requirements.lock ./
RUN pip install --no-cache-dir --prefix=/install -r requirements.lock

FROM docker.io/library/python:3.12-slim
LABEL org.opencontainers.image.title="Prototipo académico de reservas"
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN groupadd -r boa && useradd -r -g boa -d /app boa
COPY --from=builder /install /usr/local
COPY app/ ./app/
COPY migrations/ ./migrations/
COPY alembic.ini ./
USER boa
EXPOSE 8000
HEALTHCHECK --interval=15s --timeout=3s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/v1/health/ready')"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]

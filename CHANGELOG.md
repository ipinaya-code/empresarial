# Changelog

Todos los cambios notables del proyecto se documentan aquí.
El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/).

## [2.0.0] — 2026-09-26

### Añadido
- **Arquitectura Clean**: Código reestructurado en capas (core, models, schemas, services, api, db)
- **CI/CD con GitHub Actions**: Pipeline de lint, test y build automatizado
- **Configuración profesional**: `.env.example`, `pyproject.toml`, `.editorconfig`
- **Datos realistas de BoA**: Aeropuertos IATA, rutas domésticas, Boeing 737-300, pasajeros bolivianos
- **Códigos PNR**: Reservas con código estilo aerolínea (ej: `BOA-A1B2C3`)
- **Health checks**: Endpoints `/health` y `/health/ready` con verificación de PostgreSQL y Valkey
- **Suite de tests profesional**: Tests unitarios, de integración y E2E con pytest
- **API versionada**: Endpoints bajo `/api/v1/`
- **Docker production-ready**: Multi-stage build, usuario no-root, healthcheck
- **Templates GitHub**: Issues (bug/feature), PR template, CODEOWNERS
- **Excepciones de dominio**: Excepciones tipadas con mapeo a HTTP
- **Logging estructurado**: JSON en producción, legible en desarrollo
- **CONTRIBUTING.md**: Guía para el equipo de contribuidores
- **Makefile profesional**: Comandos con ayuda contextual

### Modificado
- **Docker Compose**: Naming consistente, healthchecks para todos los servicios, red dedicada
- **Modelos**: Campos extendidos (apellido, documento, nacionalidad, clase de servicio, PNR)
- **Schemas**: Validación más estricta con ejemplos y constraints
- **Diagramas**: Actualizados con nueva arquitectura

### Obsoleto
- `app/database.py`: Reemplazado por `app/db/session.py` y `app/db/cache.py` (shim de compatibilidad disponible)
- `requirements.txt`: Reemplazado por `pyproject.toml` (mantenido por retrocompatibilidad de Docker)

## [1.0.0] — 2026-09-25

### Añadido
- Prototipo transaccional de reserva de vuelos
- Control de concurrencia con `SELECT FOR UPDATE`
- Reservas provisionales con TTL
- Patrón CQRS con endpoint de lectura
- Caché con Valkey
- Pruebas de carga con K6
- Documentación y diagramas (ER, secuencia, flujo)
- Docker Compose con PostgreSQL, Valkey y API

# ─────────────────────────────────────────────────────────────
# Makefile — Sistema de Reservas BoA
# Automatización de tareas de desarrollo
# ─────────────────────────────────────────────────────────────

.PHONY: help setup install lint format test test-unit test-integration run \
	build compose-up compose-down compose-logs seed reset stress-test \
	clean db-start db-stop

# Variables
PYTHON       := python3
VENV         := .venv
PIP          := $(VENV)/bin/pip
PYTEST       := $(VENV)/bin/pytest
UVICORN      := $(VENV)/bin/uvicorn
RUFF         := $(VENV)/bin/ruff
BLACK        := $(VENV)/bin/black

DB_CONTAINER := boa-postgres
API_IMAGE    := boa-reservas-api
COMPOSE_FILE := docker/docker-compose.yml
API_URL      := http://localhost:8000

# ── Ayuda ─────────────────────────────────────────────────────
help: ## Muestra esta ayuda
	@echo ""
	@echo "  Sistema de Reservas BoA — Comandos disponibles"
	@echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""

# ── Setup ─────────────────────────────────────────────────────
setup: ## Crea entorno virtual e instala todas las dependencias
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev]"
	@echo "✅ Entorno listo. Activa con: source $(VENV)/bin/activate"

install: ## Instala solo las dependencias de producción
	$(PIP) install -e .

# ── Calidad de código ────────────────────────────────────────
lint: ## Ejecuta el linter (Ruff)
	$(RUFF) check app/ tests/

format: ## Formatea el código (Black + Ruff fix)
	$(BLACK) app/ tests/
	$(RUFF) check --fix app/ tests/

# ── Tests ─────────────────────────────────────────────────────
test: ## Ejecuta todos los tests con cobertura
	$(PYTEST) -v --tb=short

test-unit: ## Ejecuta solo los tests unitarios
	$(PYTEST) tests/unit/ -v

test-integration: ## Ejecuta solo los tests de integración
	$(PYTEST) tests/integration/ -v

test-e2e: ## Ejecuta solo los tests end-to-end
	$(PYTEST) tests/e2e/ -v

# ── Servidor local ───────────────────────────────────────────
run: ## Inicia la API en modo desarrollo
	$(UVICORN) app.main:app --host 127.0.0.1 --port 8000 --reload

# ── Docker ────────────────────────────────────────────────────
build: ## Construye la imagen Docker de la API
	docker build -f docker/Dockerfile -t $(API_IMAGE) .

compose-up: ## Levanta todo el entorno (PostgreSQL + Valkey + API)
	docker compose -f $(COMPOSE_FILE) up -d --build
	@echo ""
	@echo "  ✅ Entorno levantado:"
	@echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "  API:        $(API_URL)/docs"
	@echo "  API (v1):   $(API_URL)/api/v1/health"
	@echo "  PostgreSQL: localhost:5455"
	@echo "  Valkey:     localhost:6379"
	@echo ""

compose-down: ## Detiene y elimina los contenedores
	docker compose -f $(COMPOSE_FILE) down

compose-logs: ## Muestra los logs del entorno Docker
	docker compose -f $(COMPOSE_FILE) logs -f

# ── Base de datos standalone ──────────────────────────────────
db-start: ## Inicia solo PostgreSQL (sin Docker Compose)
	docker run -d --name $(DB_CONTAINER) \
		-e POSTGRES_USER=boa_admin \
		-e POSTGRES_PASSWORD=boa_s3cur3_p4ss \
		-e POSTGRES_DB=boa_reservas \
		-p 5455:5432 \
		docker.io/library/postgres:15

db-stop: ## Detiene PostgreSQL standalone
	docker rm -f $(DB_CONTAINER) || true

# ── Datos de prueba ──────────────────────────────────────────
seed: ## Inicializa datos de demostración de BoA
	curl -s -X POST $(API_URL)/admin/seed | python3 -m json.tool

reset: ## Resetea reservas y libera asientos
	curl -s -X POST $(API_URL)/admin/reset | python3 -m json.tool

# ── Pruebas de estrés ────────────────────────────────────────
stress-test: ## Ejecuta pruebas de carga con K6
	k6 run scripts/load_test_k6.js

# ── Limpieza ──────────────────────────────────────────────────
clean: ## Limpia artefactos generados
	rm -rf __pycache__ .pytest_cache .mypy_cache .ruff_cache htmlcov
	rm -rf *.egg-info dist build
	rm -f coverage.xml test.db
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Limpieza completada"

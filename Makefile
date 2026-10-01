.DEFAULT_GOAL := help
PYTHON ?= python3
VENV ?= .venv
PY := $(VENV)/bin/python
CONTAINER_ENGINE ?= podman
COMPOSE ?= $(CONTAINER_ENGINE) compose
COMPOSE_FILE := docker/docker-compose.yml
API_URL ?= http://127.0.0.1:8000
API_IMAGE ?= localhost/boa-reservas:dev
TEST_DATABASE_URL ?= postgresql+psycopg2://boa_test:local-test-only@127.0.0.1:55432/boa_test
K6 ?= $(CONTAINER_ENGINE) run --rm --network=host -i docker.io/grafana/k6:1.2.3
VUS ?= 50
DURATION ?= 15s
.PHONY: help setup install lint format test test-unit test-integration test-e2e test-postgres test-browser browser-install check docs-check run migrate build compose-up compose-down compose-logs seed stress-test clean
help: ## Lista comandos; Podman es el motor predeterminado
	@awk 'BEGIN {FS=":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "%-22s %s\n", $$1, $$2}' $(MAKEFILE_LIST)
setup: ## Instala el entorno reproducible de desarrollo (Python 3.12 recomendado)
	$(PYTHON) -m venv $(VENV)
	$(PY) -m pip install -r requirements-dev.lock
	$(PY) -m pip install --no-deps -e .
install: ## Instala dependencias de ejecución fijadas
	$(PY) -m pip install -r requirements.lock
	$(PY) -m pip install --no-deps -e .
lint: ## Verifica estilo sin modificar archivos
	$(PY) -m ruff check app tests scripts migrations
	$(PY) -m black --check app tests scripts migrations
format: ## Aplica formato y correcciones de estilo
	$(PY) -m ruff check --fix app tests scripts migrations
	$(PY) -m black app tests scripts migrations
test: ## Suite rápida con SQLite; no demuestra bloqueo de PostgreSQL
	$(PY) -m pytest -m 'not postgres and not browser' --junitxml=artifacts/pytest-sqlite.xml
test-unit: ## Pruebas unitarias
	$(PY) -m pytest tests/unit --no-cov
test-integration: ## Contratos HTTP sobre SQLite
	$(PY) -m pytest tests/integration --no-cov
test-e2e: ## Recorrido API (sin navegador)
	$(PY) -m pytest tests/e2e --no-cov
test-postgres: ## Suite sobre base descartable boa_test; requiere PostgreSQL
	TEST_DATABASE_URL='$(TEST_DATABASE_URL)' $(PY) -m pytest -m 'not browser' --junitxml=artifacts/pytest-postgres.xml --cov-report=xml:artifacts/coverage.xml
browser-install: ## Instala Playwright y Chromium
	$(PY) -m pip install -r requirements-browser.lock
	$(PY) -m playwright install chromium
test-browser: ## Smoke real de navegador contra API ya levantada
	BROWSER_API_URL='$(API_URL)' $(PY) -m pytest tests/browser -m browser --no-cov --tracing=retain-on-failure --screenshot=only-on-failure --output=artifacts/playwright --junitxml=artifacts/playwright.xml
docs-check: ## Verifica enlaces locales de Markdown
	$(PY) scripts/check_docs.py
check: lint docs-check test ## Puerta local de calidad
run: ## API de desarrollo (ejecutar make migrate antes)
	$(PY) -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
migrate: ## Aplica migraciones Alembic
	$(PY) -m alembic upgrade head
build: ## Construye imagen OCI con Podman
	$(CONTAINER_ENGINE) build -f docker/Dockerfile -t $(API_IMAGE) .
compose-up: ## Despliega laboratorio local con migración y servicios
	$(COMPOSE) -f $(COMPOSE_FILE) up -d --build
compose-down: ## Detiene laboratorio conservando sus volúmenes
	$(COMPOSE) -f $(COMPOSE_FILE) down
compose-logs: ## Logs del laboratorio
	$(COMPOSE) -f $(COMPOSE_FILE) logs -f
seed: ## Carga datos sintéticos (solo desarrollo con rutas demo habilitadas)
	curl --fail-with-body -sS -X POST $(API_URL)/api/v1/admin/seed
stress-test: ## Carga de lectura; JSON en artifacts/k6-summary.json
	mkdir -p artifacts
	$(K6) run --quiet --env API_URL=$(API_URL) --env VUS=$(VUS) --env DURATION=$(DURATION) - < scripts/load_test_k6.js > artifacts/k6-summary.json
clean: ## Elimina solo reportes y cachés del proyecto
	rm -rf .pytest_cache .ruff_cache .mypy_cache htmlcov artifacts test-results
	rm -f .coverage coverage.xml test.db

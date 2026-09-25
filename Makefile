.PHONY: setup start-db stop-db run test build run-container stop-container clean compose-up compose-down

# Variables
DB_CONTAINER_NAME=postgres-reserva
APP_CONTAINER_NAME=reserva-api
APP_IMAGE_NAME=reserva-vuelos-api
DB_USER=admin
DB_PASSWORD=admin
DB_NAME=reservas_db
DB_PORT=5455

setup:
	python3 -m venv venv
	./venv/bin/pip install -r requirements.txt

start-db:
	podman run -d --name $(DB_CONTAINER_NAME) -e POSTGRES_USER=$(DB_USER) -e POSTGRES_PASSWORD=$(DB_PASSWORD) -e POSTGRES_DB=$(DB_NAME) -p $(DB_PORT):5432 docker.io/library/postgres:15

stop-db:
	podman rm -f $(DB_CONTAINER_NAME) || true

run:
	./venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000

test:
	./venv/bin/python tests/test_concurrency.py

stress-test:
	k6 run scripts/load_test_k6.js

build:
	podman build -f docker/Dockerfile -t $(APP_IMAGE_NAME) .

run-container:
	podman run -d --name $(APP_CONTAINER_NAME) --network host -e DATABASE_URL="postgresql://$(DB_USER):$(DB_PASSWORD)@127.0.0.1:$(DB_PORT)/$(DB_NAME)" $(APP_IMAGE_NAME)

stop-container:
	podman rm -f $(APP_CONTAINER_NAME) || true

clean: stop-container stop-db

compose-up:
	podman-compose -f docker/docker-compose.yml up -d --build

compose-down:
	podman-compose -f docker/docker-compose.yml down

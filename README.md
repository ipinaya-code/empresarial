# Prototipo académico de reservas e inventario aéreo

Estudio de caso inspirado en observaciones reportadas sobre BoA, desarrollado por el Grupo 2 — Firefox. **No es un sistema oficial, una auditoría de BoA ni una implementación certificada de IATA.** Vuelos, pasajeros, demanda y resultados de laboratorio son sintéticos. No se dispone de telemetría, código ni datos internos de la institución.

El problema técnico que se investiga es la asignación concurrente de un mismo asiento y el comportamiento de la consulta de disponibilidad bajo carga. PostgreSQL decide la asignación; la disponibilidad que ve el usuario es orientativa y se revalida al reservar.

## Estado y documentación

La fuente de alcance son las matrices académicas conservadas en `docs/entregables/`. El [índice documental](docs/README.md) reúne investigación, requisitos, decisiones, plan y evidencias.

| Objetivo original | Alcance | Entrega |
|---|---|---|
| 1 | Bloqueo transaccional e integridad | Implementación y pruebas sobre PostgreSQL; [informe](docs/entregables/objetivos_1_2.md) |
| 2 | Refactorización de disponibilidad | Baseline reproducible y consulta optimizada; [protocolo](docs/testing/protocolo_pruebas_estres.md) y resultados en el informe |
| 3 | Caché intermedia e invalidación | Integración preliminar existente, desactivada por defecto; validación pendiente |
| 4 | Estrés periódico y capacidad | Herramientas y plan preparados; campaña final pendiente |

Frontend, pagos simulados, check-in y boletos son ampliaciones opcionales; no sustituyen los objetivos 3 y 4. Ningún resultado local implica aceptación docente, un SLA institucional o autorización de producción.

## Arranque con Podman

Requisitos: Linux, Git, Make, Podman rootless y un proveedor Compose (`podman-compose`); Python 3.12 para pruebas locales. Docker también puede usarse con `CONTAINER_ENGINE=docker`.

```bash
make compose-up
make seed
curl --fail http://127.0.0.1:8000/api/v1/health/ready
```

API: `http://127.0.0.1:8000/docs`. Compose aplica Alembic antes de iniciar dos workers. Los puertos publicados escuchan únicamente en loopback; PostgreSQL usa 5455. Valkey queda en la red interna. `make compose-down` conserva los datos. Los valores de Compose son exclusivos del laboratorio.

Para trabajar en el host:

```bash
make setup PYTHON=python3.12
cp .env.example .env
# Con PostgreSQL accesible según .env:
make migrate
make run
```

Compose define sus variables por separado de `.env` de la aplicación. Para cambiar su modo de lectura: `READ_MODE=baseline make compose-up`; para el objetivo 3: `CACHE_ENABLED=true make compose-up`. Ver [operación](docs/operacion/despliegue.md).

## Verificación

```bash
make check                         # estilo, enlaces y suite SQLite
# Base aislada: no usa el volumen del laboratorio
podman run -d --name empresarial-test-db \
  -e POSTGRES_USER=boa_test -e POSTGRES_PASSWORD=local-test-only \
  -e POSTGRES_DB=boa_test -p 127.0.0.1:55432:5432 \
  docker.io/library/postgres:15-alpine
make test-postgres                 # esperar a pg_isready si acaba de arrancar
make browser-install
make test-browser                  # API local levantada; Chromium real
make stress-test VUS=50 DURATION=15s
```

La suite PostgreSQL acepta solamente una base llamada `boa_test` y recrea sus tablas. Nunca apuntar `TEST_DATABASE_URL` a datos que deban conservarse. SQLite comprueba contratos; no demuestra `FOR UPDATE`.

Playwright comprueba el acceso desde Chromium a la API. Aún no existe una interfaz de pasajeros y no se declara validado su recorrido visual. k6 mide carga; Playwright comprueba interacción de navegador. Los resultados generados van a `artifacts/`; las evidencias seleccionadas y revisadas, a `docs/evidencias/`.

## Estructura

```text
app/                 API, servicios, modelos, configuración y persistencia
migrations/          esquema versionado con Alembic
tests/              unitarias, integración, recorrido API, PostgreSQL y navegador
scripts/             herramientas de medición y control documental
docker/              imagen OCI y Compose para Podman o Docker
.github/             CI y plantillas de revisión
docs/                planificación, arquitectura, evidencias y operación
```

Consultar [CONTRIBUTING](CONTRIBUTING.md), [seguridad](SECURITY.md) y [plan maestro](docs/planificacion/plan_maestro_boa.md). Se conserva la licencia MIT declarada originalmente en el proyecto y se añade su [texto](LICENSE). El nombre BoA y las referencias a terceros no implican afiliación ni permiso de marca.

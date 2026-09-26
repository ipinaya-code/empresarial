# ✈️ Sistema de Reservas — Boliviana de Aviación (BoA)

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![CI](https://img.shields.io/badge/CI-GitHub_Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)

**Prototipo de sistema de reservas con control de concurrencia transaccional**

[Documentación](#-documentación) · [Inicio Rápido](#-inicio-rápido) · [API](#-endpoints-de-la-api) · [Arquitectura](#-arquitectura) · [Contribuir](CONTRIBUTING.md)

</div>

---

## 📋 Descripción

Este proyecto implementa un prototipo del sistema de reservas de vuelos de **Boliviana de Aviación (BoA)**, enfocado en demostrar cómo controlar la **concurrencia al asignar asientos** y prevenir condiciones de carrera (*race conditions*).

### ¿Qué resuelve?

Cuando cientos de pasajeros intentan reservar el mismo asiento de un vuelo en oferta ("Vuelos Azules"), el sistema debe garantizar que:

- ✅ Solo **un pasajero** obtenga cada asiento
- ✅ No haya **sobreasignaciones** (overbooking no deseado)
- ✅ Las **reservas provisionales** expiren si no se confirman
- ✅ Las **consultas masivas** no bloqueen las transacciones de compra

### Estándares Implementados

| Estándar | Implementación |
|----------|---------------|
| **IATA NDC** | Offer Validity Windows → Reserva provisional con TTL |
| **IATA ONE Order** | Código PNR centralizado (`BOA-A1B2C3`) |
| **CQRS** | Lecturas cacheadas en Valkey, escrituras con locks en PostgreSQL |
| **ACID** | Transacciones con `SELECT FOR UPDATE` (bloqueo pesimista) |
| **12-Factor App** | Configuración por variables de entorno |

## 👥 Equipo

| Integrante | Rol | Épica |
|-----------|-----|-------|
| **Iver Pinaya** | Líder Backend / DBA | Epic 1: Control Transaccional |
| **Thiago Sossa** | Arquitecto de Software / DevOps | Epic 2: Refactorización CQRS |
| **Nataly Crespo** | Ingeniera de Software / DBA | Epic 3: Caché Valkey |
| **Wilson Gonzales** | Líder de QA / Rendimiento | Epic 4: Pruebas de Estrés |

## 🚀 Inicio Rápido

### Con Docker (recomendado)

```bash
# 1. Clonar el repositorio
git clone https://github.com/ipinaya-code/empresarial.git
cd empresarial

# 2. Levantar todo el entorno
make compose-up

# 3. Inicializar datos de demostración de BoA
make seed

# 4. Abrir la documentación interactiva
xdg-open http://localhost:8000/docs
```

### Sin Docker (desarrollo local detallado)

Para desarrollar localmente sin Docker Compose, sigue estos pasos:

1. **Clonar y preparar el entorno virtual:**
```bash
git clone https://github.com/ipinaya-code/empresarial.git
cd empresarial
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev]"
```

2. **Configurar variables de entorno:**
```bash
cp .env.example .env
# Edita .env si es necesario para ajustar los accesos locales
```

3. **Iniciar servicios dependientes:**
```bash
# Iniciar PostgreSQL localmente
make db-start

# (Opcional) Si necesitas Valkey/Redis para la caché
docker run -d --name boa-valkey -p 6379:6379 valkey/valkey:7.2
```

4. **Ejecutar migraciones y semilla de datos (si usas Alembic en el futuro):**
```bash
# Por ahora el seed inicializa directamente usando el backend
make run
# Y en otra terminal:
make seed
```

5. **Iniciar la API:**
```bash
make run
# La API estará disponible en http://localhost:8000
```

## 🏗️ Arquitectura

```
┌──────────────────────────────────────────────────────────┐
│                    Cliente HTTP                          │
│              (curl, httpx, navegador, K6)                │
└─────────────────────┬────────────────────────────────────┘
                      │ HTTP :8000
┌─────────────────────▼────────────────────────────────────┐
│                  FastAPI (Uvicorn)                        │
│  ┌─────────────────────────┐  ┌────────────────────────┐ │
│  │  📖 QUERIES (Lecturas)  │  │  ✏️ COMMANDS (Escritura)│ │
│  │  GET /vuelos/disp.      │  │  POST /reservar/*      │ │
│  │  Sin bloqueos           │  │  SELECT FOR UPDATE     │ │
│  └──────────┬──────────────┘  └──────────┬─────────────┘ │
│             │                            │               │
│  ┌──────────▼──────────┐   ┌─────────────▼───────────┐   │
│  │    Valkey (Caché)    │   │    PostgreSQL 15        │   │
│  │    TTL: 10 min       │   │    Transacciones ACID   │   │
│  │    Cache Hit/Miss    │   │    Bloqueo pesimista    │   │
│  └─────────────────────┘   └─────────────────────────┘   │
└──────────────────────────────────────────────────────────┘
```

Para diagramas detallados ver:
- [Arquitectura del Sistema (C4)](docs/arquitectura/arquitectura_sistema.md)
- [Diagrama ER Extendido](docs/diagramas/diagrama_er.md)
- [Diagramas de Secuencia](docs/diagramas/diagrama_secuencia_reserva.md)

### Tecnologías

| Componente | Tecnología | Versión |
|-----------|-----------|---------|
| API | FastAPI + Uvicorn | 0.110+ |
| ORM | SQLAlchemy | 2.0+ |
| Base de datos | PostgreSQL | 15 |
| Caché | Valkey | 7.2 |
| Contenedores | Docker Compose | v2 |
| Tests | Pytest | 8.0+ |
| Linting | Ruff + Black | Latest |
| CI/CD | GitHub Actions | v4 |
| Load Testing | Grafana K6 | Latest |

## 📁 Estructura del Proyecto

```
empresarial/
├── app/
│   ├── core/                  # Configuración, excepciones, logging
│   │   ├── config.py          # Pydantic Settings (env vars)
│   │   ├── exceptions.py      # Excepciones de dominio tipadas
│   │   └── logging.py         # Logging estructurado
│   ├── models/                # Modelos SQLAlchemy
│   │   ├── usuario.py         # Pasajero (CI, nacionalidad)
│   │   ├── vuelo.py           # Vuelo (IATA, Boeing 737-300)
│   │   ├── asiento.py         # Asiento (clase, estado)
│   │   └── reserva.py         # Reserva (PNR, TTL)
│   ├── schemas/               # Validación Pydantic
│   ├── services/              # Lógica de negocio
│   │   ├── reserva_service.py # Flujos de reserva (inseguro/seguro/provisional)
│   │   ├── disponibilidad_service.py  # CQRS: lecturas + caché
│   │   └── seed_service.py    # Datos realistas de BoA
│   ├── api/v1/                # Routers FastAPI
│   │   ├── reservas.py        # Endpoints de escritura
│   │   ├── vuelos.py          # Endpoints de lectura
│   │   ├── admin.py           # Seed y reset
│   │   └── health.py          # Health checks
│   ├── db/                    # Sesión de BD y caché
│   └── main.py                # App factory
├── tests/
│   ├── unit/                  # Tests unitarios
│   ├── integration/           # Tests con BD
│   └── e2e/                   # Tests de flujo completo
├── docker/
│   ├── Dockerfile             # Multi-stage (builder + runtime)
│   └── docker-compose.yml     # PostgreSQL + Valkey + API
├── scripts/
│   └── load_test_k6.js        # Pruebas de carga K6
├── docs/                      # Documentación y diagramas
├── .github/
│   ├── workflows/ci.yml       # Pipeline CI/CD
│   ├── CODEOWNERS             # Responsables por área
│   └── PULL_REQUEST_TEMPLATE.md
├── pyproject.toml             # Configuración del proyecto
├── Makefile                   # Automatización de tareas
├── CONTRIBUTING.md            # Guía de contribución
├── CHANGELOG.md               # Historial de cambios
└── .env.example               # Variables de entorno
```

## 🔌 Endpoints de la API

### `v1` — Endpoints principales (`/api/v1/`)

| Método | Endpoint | Descripción | Patrón |
|--------|----------|-------------|--------|
| `GET` | `/api/v1/health` | Health check básico | — |
| `GET` | `/api/v1/health/ready` | Readiness check (PG + Valkey) | — |
| `POST` | `/api/v1/admin/seed` | Inicializar datos BoA | Admin |
| `POST` | `/api/v1/admin/reset` | Resetear reservas | Admin |
| `GET` | `/api/v1/vuelos/{id}/disponibilidad` | Disponibilidad de asientos | CQRS: Query |
| `POST` | `/api/v1/reservar/inseguro` | Reserva SIN bloqueo (demo) | CQRS: Command |
| `POST` | `/api/v1/reservar/seguro` | Reserva CON `SELECT FOR UPDATE` | CQRS: Command |
| `POST` | `/api/v1/reservar/provisional` | Reserva temporal (TTL 10min) | CQRS: Command |
| `POST` | `/api/v1/reservar/{id}/confirmar` | Confirmar reserva provisional | CQRS: Command |
| `POST` | `/api/v1/reservar/expirar` | Expirar reservas vencidas | CQRS: Command |

### Documentación Interactiva

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 🔄 Flujo Transaccional

### Ciclo de vida de un asiento

```
DISPONIBLE ──────► RESERVADO_PROVISIONAL ──────► CONFIRMADO
     ▲                      │
     │                      │ (expira TTL)
     └──────────────────────┘
```

### Comparación de flujos

| Aspecto | Sin Control | Con `SELECT FOR UPDATE` |
|---------|------------|------------------------|
| Bloqueo de fila | ❌ No | ✅ Sí |
| Espera simulada | 0.5s | 60s |
| Race condition | ⚠️ Posible | ✅ Prevenida |
| Sobreasignación | ⚠️ Posible (protegida por índice) | ✅ Imposible |
| Resultado con 5 solicitudes | Puede tener >1 éxito HTTP | Exactamente 1 éxito |

## 🧪 Tests

```bash
make test              # Todos los tests con cobertura
make test-unit         # Solo unitarios (modelos, schemas)
make test-integration  # Con base de datos (endpoints)
make test-e2e          # Flujo completo de pasajero
make stress-test       # Pruebas de carga con K6 (500 VU)
```

## 📊 Datos Simulados de BoA

El seed genera datos realistas basados en la operación real de BoA:

- **12 rutas domésticas** (VVI↔LPB, VVI↔CBB, LPB↔CBB, etc.)
- **Boeing 737-300**: 18 asientos ejecutiva + 114 económica = 132 por vuelo
- **20 pasajeros** con nombres y documentos bolivianos
- **Horarios realistas**: 06:00, 08:30, 12:00, 15:30, 19:00
- **Códigos IATA**: Vuelos `OB-100` a `OB-111`, PNR `BOA-XXXXXX`

## 📖 Documentación

| Documento | Descripción |
|-----------|-------------|
| [Arquitectura del Sistema](docs/arquitectura/arquitectura_sistema.md) | Diagramas C4, CQRS, deployment |
| [Diagrama ER](docs/diagramas/diagrama_er.md) | Modelo de datos con campos IATA |
| [Diagramas de Secuencia](docs/diagramas/diagrama_secuencia_reserva.md) | Flujos seguro, provisional, inseguro |
| [Arquitectura CQRS](docs/arquitectura/arquitectura_cqrs_objetivo_2.md) | Justificación del patrón CQRS |
| [Estándares IATA](docs/planificacion/investigacion_estandares_boa.md) | NDC, ONE Order, patrones de concurrencia |
| [Plan de Ejecución](docs/planificacion/plan_ejecucion_prototipo_boa.md) | Backlog completo por épica |
| [Protocolo de Estrés](docs/testing/protocolo_pruebas_estres.md) | SLAs, rampas de carga, criterios |
| [Evidencia de Pruebas](docs/testing/evidencia_pruebas.md) | Cómo ejecutar y validar |
| [Guía de Logs](docs/testing/como_generar_logs.md) | Generación de evidencia |
| [Plan Maestro BoA](docs/planificacion/plan_maestro_boa.md) | Planeación General |

## 🛠️ Cómo Extender e Implementar Nuevas Funcionalidades

Si deseas continuar el desarrollo o implementar nuevas características:

1. **Crear nuevos Modelos (`app/models/`)**: Define tus entidades de SQLAlchemy. Recuerda que si manejas concurrencia, usarás bloqueos o CQRS.
2. **Definir Schemas (`app/schemas/`)**: Usa Pydantic (V2 con `model_config`) para validar la entrada (Create) y salida (Response).
3. **Lógica en Servicios (`app/services/`)**: Coloca aquí la lógica de negocio, transacciones, y llamadas a caché. Mantén los Routers limpios.
4. **Endpoints en Routers (`app/api/v1/`)**: Expón tus servicios mediante FastAPI. 
5. **Escribir Tests (`tests/`)**: Añade tests unitarios (sin DB) o de integración (con BD usando el `TestClient`).
6. **Formateo y Linting**: Antes de hacer commit, ejecuta `make format` y `make lint`.

## 🤝 Contribuir

Ver [CONTRIBUTING.md](CONTRIBUTING.md) para la guía completa del equipo.

## 📄 Licencia

Este proyecto es un prototipo académico/técnico. Los datos son simulados y no representan información real de Boliviana de Aviación.

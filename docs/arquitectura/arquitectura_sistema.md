# Diagrama de Arquitectura del Sistema

## Arquitectura de Alto Nivel (C4 — Context)

```mermaid
C4Context
    title Sistema de Reservas BoA — Diagrama de Contexto

    Person(pasajero, "Pasajero", "Usuario que busca y reserva vuelos")
    Person(admin, "Administrador", "Opera y monitorea el sistema")

    System(boa_system, "Sistema de Reservas BoA", "Gestiona la disponibilidad y reserva de asientos con control de concurrencia")

    System_Ext(iata_ndc, "IATA NDC", "Estándar de distribución de contenido aéreo")
    System_Ext(payment, "Gateway de Pagos", "Procesamiento de pagos (futuro)")

    Rel(pasajero, boa_system, "Busca vuelos, reserva asientos", "HTTPS/JSON")
    Rel(admin, boa_system, "Monitorea, seed, reset", "HTTPS/JSON")
    Rel(boa_system, iata_ndc, "Alineado con estándares", "Referencia")
    Rel(boa_system, payment, "Confirma pago (futuro)", "HTTPS")
```

## Arquitectura de Contenedores (C4 — Container)

```mermaid
C4Container
    title Sistema de Reservas BoA — Contenedores

    Person(pasajero, "Pasajero")

    Container_Boundary(boa, "Sistema de Reservas BoA") {
        Container(api, "API FastAPI", "Python 3.11, Uvicorn", "API REST con control de concurrencia ACID")
        ContainerDb(postgres, "PostgreSQL 15", "Base de Datos", "Almacenamiento transaccional con SELECT FOR UPDATE")
        ContainerDb(valkey, "Valkey 7.2", "Caché", "Cache de lecturas CQRS con TTL")
    }

    Rel(pasajero, api, "HTTP/JSON", "Buscar vuelos, reservar")
    Rel(api, postgres, "SQL", "Escrituras transaccionales con locks")
    Rel(api, valkey, "Redis Protocol", "Lectura cacheada, invalidación")
```

## Flujo CQRS (Command Query Responsibility Segregation)

```mermaid
flowchart LR
    subgraph QUERIES["📖 Lecturas (Query Side)"]
        Q1["GET /vuelos/{id}/disponibilidad"]
        Q1 --> CACHE{"¿Cache Hit?"}
        CACHE -->|Sí| RESP1["Respuesta desde Valkey"]
        CACHE -->|No| REPLICA["PostgreSQL (sin locks)"]
        REPLICA --> CACHE_SET["Escribir en Valkey"]
        CACHE_SET --> RESP1
    end

    subgraph COMMANDS["✏️ Escrituras (Command Side)"]
        C1["POST /reservar/seguro"]
        C1 --> LOCK["SELECT ... FOR UPDATE"]
        LOCK --> VALIDATE["Validar disponibilidad"]
        VALIDATE --> COMMIT["INSERT + COMMIT"]
        COMMIT --> INVALIDATE["Invalidar caché"]
    end

    style QUERIES fill:#e8f5e9,stroke:#2e7d32
    style COMMANDS fill:#fff3e0,stroke:#e65100
```

## Diagrama de Deployment (Docker Compose)

```mermaid
flowchart TB
    subgraph DOCKER["Docker Compose — boa-network"]
        direction TB

        subgraph API_CONTAINER["📦 boa-api"]
            API["FastAPI + Uvicorn<br/>Puerto 8000<br/>2 workers"]
        end

        subgraph PG_CONTAINER["📦 boa-postgres"]
            PG["PostgreSQL 15<br/>Puerto 5455:5432<br/>Volume: db_data"]
        end

        subgraph VK_CONTAINER["📦 boa-valkey"]
            VK["Valkey 7.2<br/>Puerto 6379<br/>Volume: valkey_data"]
        end

        API -->|"SQL (psycopg2)"| PG
        API -->|"Redis Protocol"| VK
    end

    CLIENT["🌐 Cliente HTTP<br/>(curl, httpx, navegador)"] -->|"HTTP :8000"| API
    K6["📊 K6 Load Test"] -->|"HTTP :8000"| API
    GHACTIONS["🔄 GitHub Actions CI"] -->|"Build & Test"| DOCKER

    style API_CONTAINER fill:#e3f2fd,stroke:#1565c0
    style PG_CONTAINER fill:#fce4ec,stroke:#c62828
    style VK_CONTAINER fill:#f3e5f5,stroke:#7b1fa2
```

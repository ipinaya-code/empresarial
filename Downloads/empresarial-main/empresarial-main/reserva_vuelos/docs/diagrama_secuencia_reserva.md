# Diagrama de secuencia de reserva

```mermaid
sequenceDiagram
    actor Cliente
    participant API as FastAPI
    participant DB as PostgreSQL

    Cliente->>API: POST /reservar/seguro
    API->>DB: BEGIN
    API->>DB: SELECT asiento FOR UPDATE
    DB-->>API: Fila bloqueada
    API->>DB: Validar usuario y estado DISPONIBLE
    Note over API,DB: Procesamiento simulado: 1 minuto (60 segundos)
    alt Asiento no disponible
        API->>DB: ROLLBACK
        API-->>Cliente: 409 Asiento no disponible
    else Asiento disponible
        Note over API,DB: Procesamiento simulado: 1 minuto (60 segundos)
        API->>DB: UPDATE asiento = CONFIRMADO
        API->>DB: INSERT reserva CONFIRMADA
        API->>DB: COMMIT
        API-->>Cliente: 200 Reserva confirmada
    end
```

El bloqueo de fila serializa las solicitudes que intentan asignar el mismo asiento. La transacción se mantiene abierta durante el procesamiento simulado de un minuto y se libera al ejecutar `COMMIT`.

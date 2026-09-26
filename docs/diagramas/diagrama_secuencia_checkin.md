# Diagramas de Secuencia — Check-in Web

## 1. Check-in Exitoso con Boarding Pass

```mermaid
sequenceDiagram
    actor P as Pasajero
    participant FE as Frontend (Navegador)
    participant API as FastAPI
    participant DB as PostgreSQL

    P->>FE: Ingresa PNR o Nº Reserva
    FE->>API: POST /api/v1/checkin/{reserva_id}

    API->>DB: BEGIN
    API->>DB: SELECT reserva FOR UPDATE<br/>WHERE id = reserva_id
    DB-->>API: reserva (estado = 'confirmada')

    Note over API: Validar: estado = CONFIRMADA

    API->>DB: SELECT usuario, asiento, vuelo<br/>(datos para boarding pass)
    DB-->>API: Datos del pasajero y vuelo

    API->>DB: UPDATE reserva SET estado = 'checked_in'
    API->>DB: UPDATE boleto SET estado = 'checked_in'
    API->>DB: COMMIT

    Note over API: Generar QR Code (base64)

    API-->>FE: ✅ HTTP 200 — Boarding Pass JSON
    FE-->>P: 🎫 Boarding Pass Visual<br/>(PNR, Vuelo, Asiento, QR)
```

## 2. Check-in Rechazado — Reserva No Confirmada

```mermaid
sequenceDiagram
    actor P as Pasajero
    participant API as FastAPI
    participant DB as PostgreSQL

    P->>API: POST /api/v1/checkin/{reserva_id}

    API->>DB: SELECT reserva WHERE id = reserva_id
    DB-->>API: reserva (estado = 'pendiente')

    Note over API: ❌ Estado no es CONFIRMADA

    API-->>P: HTTP 409 — Reserva no modificable<br/>(debe confirmar primero)
```

## 3. Check-in Rechazado — Ya Realizado

```mermaid
sequenceDiagram
    actor P as Pasajero
    participant API as FastAPI
    participant DB as PostgreSQL

    P->>API: POST /api/v1/checkin/{reserva_id}

    API->>DB: SELECT reserva WHERE id = reserva_id
    DB-->>API: reserva (estado = 'checked_in')

    Note over API: ❌ Ya realizó check-in

    API-->>P: HTTP 409 — Reserva no modificable<br/>(check-in ya realizado)
```

## Datos del Boarding Pass

El boarding pass generado contiene:

| Campo | Ejemplo | Fuente |
|-------|---------|--------|
| PNR | BOA-A1B2C3 | `reservas.codigo_reserva` |
| Nº Boleto | 930-1234567890 | `boletos.numero_boleto` |
| Pasajero | Juan Mamani | `usuarios.nombre + apellido` |
| Documento | CI 12345678 | `usuarios.documento_tipo + numero` |
| Vuelo | OB-101 | `vuelos.codigo` |
| Origen → Destino | VVI → LPB | `vuelos.origen_iata → destino_iata` |
| Fecha | 2026-10-15 06:00 | `vuelos.fecha_salida` |
| Asiento | 14A | `asientos.numero` |
| Clase | Económica | `asientos.clase` |
| Grupo Embarque | B | Calculado (A=ejecutiva, B=económica) |
| Puerta | 12 | Asignado por el sistema |
| QR Code | base64(...) | JSON codificado con datos clave |

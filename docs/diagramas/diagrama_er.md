# Diagrama Entidad-Relación (v2.0)

## Modelo de Datos — Sistema de Reservas BoA

```mermaid
erDiagram
    USUARIOS ||--o{ RESERVAS : "realiza"
    VUELOS ||--|{ ASIENTOS : "contiene"
    ASIENTOS ||--o{ RESERVAS : "asigna"

    USUARIOS {
        int id PK
        string nombre "Nombre del pasajero"
        string apellido "Apellido del pasajero"
        string email UK "Correo electronico unico"
        string documento_tipo "CI, PASAPORTE, DNI"
        string documento_numero UK "Numero de documento"
        string telefono "Telefono de contacto"
        string nacionalidad "Codigo ISO 3166 alpha-3"
    }

    VUELOS {
        int id PK
        string codigo UK "Codigo IATA del vuelo (OB-101)"
        string origen_iata "Codigo IATA origen (VVI)"
        string origen_nombre "Nombre del aeropuerto"
        string destino_iata "Codigo IATA destino (LPB)"
        string destino_nombre "Nombre del aeropuerto"
        datetime fecha_salida "Fecha y hora de salida"
        datetime fecha_llegada "Fecha y hora de llegada"
        string aeronave "Boeing 737-300"
        int capacidad "Capacidad total"
        string estado "PROGRAMADO, EN_VUELO, etc"
    }

    ASIENTOS {
        int id PK
        int vuelo_id FK "Referencia al vuelo"
        string numero "Identificador (ej: 1A, 14F)"
        int fila "Numero de fila (1-22)"
        string columna "Letra de columna (A-F)"
        enum clase "ejecutiva o economica"
        enum estado "disponible, reservado_provisional, confirmado, bloqueado"
        datetime fecha_expiracion "Limite de reserva provisional"
    }

    RESERVAS {
        int id PK
        string codigo_reserva UK "Codigo PNR (BOA-A1B2C3)"
        int usuario_id FK "Referencia al pasajero"
        int asiento_id FK "Referencia al asiento"
        datetime fecha_reserva "Fecha de creacion"
        datetime fecha_expiracion "Limite para confirmar"
        enum estado "pendiente, confirmada, cancelada"
    }
```

## Reglas de Integridad

1. **Índice único parcial**: Un asiento puede tener como máximo **una** reserva activa (`pendiente` o `confirmada`). Las reservas `cancelada` permanecen como historial.

2. **Claves foráneas**:
   - `asientos.vuelo_id → vuelos.id` (CASCADE DELETE)
   - `reservas.usuario_id → usuarios.id` (RESTRICT)
   - `reservas.asiento_id → asientos.id` (RESTRICT)

3. **Códigos únicos**: `vuelos.codigo` y `reservas.codigo_reserva` son únicos globalmente.

## Configuración del Boeing 737-300 de BoA

| Clase | Filas | Columnas | Asientos |
|-------|-------|----------|----------|
| Ejecutiva | 1-3 | A-F (3-3) | 18 |
| Económica | 4-22 | A-F (3-3) | 114 |
| **Total** | | | **132** |

## Aeropuertos de Bolivia (IATA)

| Código | Aeropuerto | Ciudad |
|--------|-----------|--------|
| VVI | Viru Viru International | Santa Cruz |
| LPB | El Alto International | La Paz |
| CBB | Jorge Wilstermann | Cochabamba |
| SRE | Alcantarí | Sucre |
| TJA | Capitán Oriel Lea Plaza | Tarija |
| ORU | Juan Mendoza | Oruro |
| TDD | Teniente Jorge Henrich Arauz | Trinidad |
| CIJ | Capitán Aníbal Arab | Cobija |

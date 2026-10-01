# Requisitos, reglas y trazabilidad

## Requisitos verificables

| ID | Objetivo | Regla / aceptación | Implementación y evidencia |
|---|---|---|---|
| RF-01 | O1 | Máximo una reserva PENDIENTE/CONFIRMADA por asiento | Índice parcial; `tests/postgres/test_integrity.py` |
| RF-02 | O1 | Diez intentos simultáneos → uno aceptado, nueve conflictos | `reservar_seguro`, `reservar_provisional`; sesiones independientes |
| RF-03 | O1 | Reserva y asiento cambian en una transacción; errores revierten | Servicios, tests y verificación SQL |
| RF-04 | O1 | Expirada no se confirma; se libera asiento y conserva historial | Pruebas de expiración/reutilización e invalidación |
| RF-05 | O2 | Baseline y refactor devuelven igual JSON para igual estado | `test_baseline_refactored_same_contract` |
| RF-06 | O2 | Lectura completa durante lock de asiento sin esperar ese lock | `test_read_does_not_wait_for_seat_lock`, timeout SQL 500 ms |
| RNF-01 | O2 | Meta de laboratorio p95 <200 ms, p99 <500 ms y errores <1% | k6 por nivel 50/200/500; no es SLA IATA |
| RNF-02 | Base | PostgreSQL inaccesible → readiness HTTP 503 sin detalles internos | `test_readiness_returns_503_without_database` |
| RNF-03 | Base | Seed/reset/inseguro/expirar solo en laboratorio explícito | Pruebas de rutas demo y modo production |
| RNF-04 | Base | Instalación fijada, esquema versionado y CI reproducible | Locks, Alembic, Makefile, workflow |
| RNF-05 | O3 | Caché desactualizada nunca autoriza una reserva | Autoridad SQL; ampliar pruebas con Valkey real |
| RNF-06 | O4 | Fallos, carga y recuperación generan artefactos comparables | Protocolo y backlog O4 |

## Reglas de dominio vigentes

`DISPONIBLE → RESERVADO_PROVISIONAL → CONFIRMADO`. Una reserva `PENDIENTE` pasa a `CONFIRMADA` o `CANCELADA` al expirar. La reserva directa segura confirma en un único paso. `BLOQUEADO` no es reservable. Se exige usuario y asiento existentes, IDs positivos y número de asiento único dentro de un vuelo.

El TTL provisional es de diez minutos por decisión académica. No existe worker de expiración todavía: la confirmación verifica vencimiento y la ruta manual de laboratorio expira reservas. O3/O4 deben decidir y probar un planificador. El TTL de caché es distinto del TTL de reserva.

Los enums SQL se guardan como nombres en mayúsculas; el JSON expone valores en minúsculas. Las fechas actuales se guardan como UTC sin zona; la migración a `timestamptz` se reserva para la ampliación de dominio y debe incluir datos anteriores.

## Contrato HTTP mínimo

| Operación | Ruta canónica | Resultado |
|---|---|---|
| Consultar | `GET /api/v1/vuelos/{id}/disponibilidad` | 200; 404 vuelo inexistente |
| Reservar | `POST /api/v1/reservar/seguro` | 200 confirmada; 409 ocupada; 404 referencia inexistente; 422 payload |
| Retener | `POST /api/v1/reservar/provisional` | 200 pendiente con fecha límite |
| Confirmar | `POST /api/v1/reservar/{id}/confirmar` | 200; 409 vencida/no pendiente |
| Readiness | `GET /api/v1/health/ready` | 200 operativo/degradado sin caché; 503 sin BD |

No hay identidad de pasajero autenticada, autorización por propietario, pago real, idempotency-key ni cancelación de usuario. Un ID o código de reserva no es una credencial. Esos requisitos bloquean exposición pública y tienen tareas explícitas en el backlog.

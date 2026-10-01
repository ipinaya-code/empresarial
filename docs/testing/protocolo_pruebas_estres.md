# Protocolo reproducible de pruebas

Versión 1, 2026-09-27. Entorno autorizado: laboratorio local y staging propio aislado. No enviar carga a sitios de BoA ni a servicios ajenos.

## Niveles y responsabilidades

| Nivel | Herramienta | Qué demuestra |
|---|---|---|
| Unitario/contrato | pytest + SQLite | Validación, errores, JSON, estados en ejecución secuencial |
| Integración real | pytest + PostgreSQL 15 | Locks, índices, concurrencia con sesiones distintas, expiración |
| Recorrido API | TestClient | Provisional → confirmar → disponibilidad; sin navegador |
| Navegador | Playwright + Chromium | Acceso HTTP desde navegador y contrato de API; UI futura por separado |
| Rendimiento O2 | k6 | Comparación baseline/refactor sin caché por nivel |
| Estrés O4 | k6 + métricas SO/BD | Capacidad mixta, duración y recuperación; pendiente |

## O1: invariante transaccional

Ejecutar `make test-postgres` con PostgreSQL descartable `boa_test`. Control negativo: cinco transacciones leen cero asignaciones y, tras barrera, insertan en tabla aislada sin locks ni unicidad. Deben producir cinco filas. Control protegido: diez intentos simultáneos por el mismo asiento, tanto seguro como provisional; exactamente un ganador, nueve conflictos y una reserva activa SQL. El control negativo demuestra el mecanismo de carrera en el laboratorio, no un incidente institucional.

También: inserción directa duplicada debe fallar por índice; expirar conserva historial y permite nueva reserva; confirmar vencida invalida caché; una lectura puede completarse mientras un escritor mantiene el lock. Incluir rollback en errores y pruebas nuevas al ampliar estados.

## O2: diseño comparativo

Variables fijas: PostgreSQL/dataset, 2 workers, caché apagada, demora segura 0, mismo host y k6. Cambiar exclusivamente `READ_MODE=baseline|refactored`. Una consulta de vuelo y una de asientos en ambos casos. Baseline materializa entidades completas; refactor selecciona columnas.

Niveles 50, 200 y 500 VU; pausa de 1 s por iteración; tres repeticiones por variante/nivel; 5 s de calentamiento separados y 15 s de medición por ejecución. Alternar orden baseline/refactored entre repeticiones. La duración es suficiente para una comparación exploratoria, no para un SLA ni prueba de resistencia. Registrar CPU/RAM del host y advertir si el generador comparte máquina.

```bash
make compose-up
make seed
# Script automatizado: ambas variantes, warm-up y JSON por ejecución
.venv/bin/python scripts/benchmark.py
```

Para repetir sin sobrescribir evidencia: añadir `--output artifacts/benchmark-NUEVA_CORRIDA`.

El script recrea únicamente el servicio API del laboratorio Compose y realiza lecturas; no elimina reservas. No ejecutar mientras otra persona usa ese laboratorio. El dato de seed debe permanecer igual. Al terminar restaura `READ_MODE=refactored` y caché apagada.

Por ejecución registrar duración, VU, p50/p95/p99, req/s, errores y checks. Gates: p95 <200 ms; p99 <500 ms; errores <1%; checks =100%. Los checks también tienen threshold para que un contrato roto produzca salida no cero. Reportar cada ejecución; resumir mediana de p95 y req/s entre repeticiones sin promediar percentiles como si fueran muestras crudas. Un 409 de concurrencia es resultado de negocio esperado en O1; no se mezcla con errores de lectura de O2.

Para una prueba puntual: `make stress-test VUS=50 DURATION=15s`. El JSON generado no constituye una comparación completa.

## O3 y O4: ampliación prevista

O3 repite con caché apagada/encendida, cuenta SQL real por operación y registra hit/miss, TTL, invalidación, reinicio y caída. No utilizar un contador declarado en JavaScript como si midiera hits del servidor. Meta de reducción de lecturas de la matriz: ≥70%, sujeta a workload definido.

O4 añade mezcla propuesta 90% consultas/10% comandos, reserva provisional y confirmación, dataset que no se agote inadvertidamente, spike y soak ≥30 minutos. Registrar CPU/RAM, conexiones, locks, timeouts, p99 y recuperación. Definir antes de ejecutar cuándo se detiene por saturación y qué conflictos se esperan. Programar en agente dedicado; no usar un runner compartido para afirmar capacidad productiva.

## Custodia

Cada corrida tiene ID, UTC, commit base, estado dirty, huellas de archivos relevantes, comandos, herramientas, ambiente, JSON/JUnit y dictamen. Conservar resultados fallidos. No publicar tokens ni datos personales. Generar el manifiesto después de copiar artefactos; revisar antes de versionar. Capturas son apoyo, no sustituyen datos y comandos.

La variante final refactorizada también declara `VueloDisponibilidadResponse` para validar y serializar con Pydantic. Baseline conserva la serialización genérica anterior. Por tanto, el tratamiento experimental combina proyección SQL y serialización tipada; no se atribuye todo el efecto a una sola técnica. Cambiar `READ_MODE` requiere reiniciar la API.

# Backlog y tareas de mantenimiento

Estados: entregado = artefacto y prueba disponible; preparado = herramienta escrita pendiente de ejecución externa; pendiente = trabajo futuro. Los responsables corresponden a roles de las matrices, no a una aceptación nueva de tareas.

## Base necesaria para continuar

| ID | Tarea | Estado / aceptación | Rol |
|---|---|---|---|
| CH-01 | Corregir alcance y afirmaciones sin respaldo | Entregado: plan, metodología y fuentes; originales preservados | Coordinación |
| CH-02 | Quitar módulos y configuración duplicados | Entregado: paquetes canónicos sin colisión | Backend |
| CH-03 | Podman por defecto, puertos locales y datos persistentes | Entregado: Compose y Make; ver evidencia de ejecución | DevOps |
| CH-04 | Fijar dependencias y esquema | Entregado: tres locks y migración inicial | DevOps/DBA |
| CH-05 | CI con PostgreSQL real | Preparado: workflow; validar ejecución remota en próximo push | DevOps |
| CH-06 | Calidad, enlaces y reportes | Entregado: Make/check y artefactos de pruebas | QA |
| CH-07 | Playwright | Entregado: smoke Chromium; UI aún sin implementar | QA |
| CH-08 | Seguridad mínima de laboratorio | Entregado: rutas demo explícitas y readiness 503 | Backend |
| CH-09 | Procedimientos de despliegue/rollback | Entregado: runbook; operación pública pendiente | DevOps |
| CH-10 | Jenkins alternativo | Preparado: Jenkinsfile; servidor/agente aún no provisionados | DevOps |
| CH-11 | Gobernanza externa | Pendiente: protección de main, permisos y aprobación docente; licencia MIT original documentada | Coordinación |
| CH-12 | Evaluar Vagrant | Decisión documentada; no requerido por la ruta Podman | DevOps |

## Cierre O1/O2

| ID | Entrega | Evidencia |
|---|---|---|
| O1-01 | Índice parcial corregido y unicidad vuelo/asiento | Modelos, Alembic y test de escritura directa |
| O1-02 | Concurrencia sobre PG con conexiones separadas | Control negativo aislado y un único ganador en rutas protegidas |
| O1-03 | Expiración, historial y liberación coherente | Reutilización de asiento, invalidación al expirar |
| O2-01 | Lecturas sin lock y baseline conservado | Modos baseline/refactored; mismo contrato |
| O2-02 | Comparación bajo carga | k6, resúmenes JSON e informe; cada meta conserva su estado real |
| O2-03 | Documentos para exposición | Informe, diagramas, matriz de trazabilidad y registro de evidencia |

## O3 — Caché (después de O2)

| ID / prioridad | Trabajo concreto | Aceptación y dependencia | Rol / estimación |
|---|---|---|---|
| O3-01 P0 | Definir TTL por dato | Disponibilidad propuesta 30 s; itinerarios/horarios 300 s; tarifas fuera de modelo. Justificar cambios | DBA, 0.5 jornada |
| O3-02 P0 | Resolver carrera de repoblado | Test fuerza lectura antigua → commit/invalidate → set antiguo; versionado o estrategia elegida mantiene política de frescura | Backend, 1–2 |
| O3-03 P0 | Probar Valkey real | Hit, miss, caída, recuperación y caché corrupta; ninguna doble asignación | QA, 1 |
| O3-04 P1 | Medir SQL y caché | Mismo workload con/sin caché, contadores SQL reales; reducción ≥70% como meta académica | QA/DBA, 1 |
| O3-05 P1 | Expiración periódica | Worker idempotente, lotes acotados, confirmación concurrente, reinicio y métricas de retraso | Backend, 1–2 |
| O3-06 P1 | Evitar cache stampede | Medir arranque frío y carga simultánea; coalescing/versionado si se necesita | Backend, 1 |

## O4 — Estrés y validación periódica

| ID / prioridad | Trabajo | Criterio | Rol / estimación |
|---|---|---|---|
| O4-01 P0 | Carga mixta con fixtures suficientes | Consulta → provisional → confirmar; separar 409 esperado de error técnico y fallar por 5xx | QA, 1 |
| O4-02 P0 | Pico y sostenimiento | Rampas, spike, soak ≥30 min; CPU/RAM, conexiones, locks, latencia y errores correlacionados | QA/DevOps, 1 |
| O4-03 P0 | Fallos y recuperación | Reiniciar API/Valkey, cortar BD controladamente; preservar invariantes y recuperar readiness | QA/DBA, 1 |
| O4-04 P1 | Repetición programada | Job manual/nocturno en staging aislado, artefactos y aviso al responsable sin datos sensibles | DevOps, 1 |
| O4-05 P0 | Informe final revisado | Todas las repeticiones, límites del hardware y dictamen por criterio | Equipo, 1 |

## Antes de una publicación real

P0: identidad y permisos por propietario (incluido acceso directo a objetos), idempotencia, rate limiting, secretos, HTTPS, proxy, rutas administrativas separadas, validación de datos y revisión ASVS. P0: base de datos con rol mínimo, migración ensayada, backup restaurado, monitoreo, responsables y respuesta a incidentes. P1: SBOM, análisis de dependencias e imagen, firma/digest, métricas, alertas y retención de logs. [Riesgos y decisiones](riesgos_decisiones.md).

Extensiones separadas: panel web accesible y pruebas Playwright del recorrido de pasajero; pagos mediante adaptador simulado sin PAN; cancelación e idempotencia; instancias de vuelo por fecha; check-in/boletos solo después de definir reglas. No se introducen números de boleto “IATA válidos” ni reglas de check-in de BoA sin especificación comprobada.

# Plan maestro y alcance controlado

Grupo 2 — Firefox. Revisión: 2026-09-27. Objetivo general académico: explorar el rediseño transaccional de reservas e inventario para prevenir asignaciones incompatibles bajo demanda sintética. Los resultados describen el prototipo, no la operación de BoA.

## Objetivos originales y secuencia

| ID | Objetivo y responsable registrado en matrices | Puerta de salida |
|---|---|---|
| O1 | Bloqueo transaccional — Iver Pinaya | ER, reglas, migración, control negativo, reserva segura concurrente, expiración y evidencia SQL |
| O2 | Refactorizar disponibilidad — Thiago Sossa | Baseline conservado, contrato equivalente, lecturas durante locks, comparación 50/200/500 VU y conclusión honesta |
| O3 | Capa de caché — Nataly Crespo | TTL por datos, invalidación, fallos de Valkey, medición de consultas SQL y latencia |
| O4 | Protocolo de estrés periódico — Wilson Gonzales | Mezcla de lecturas/escrituras, ráfagas, duración sostenida, recursos, recuperación y reporte revisado |

El plan anterior reasignaba O3 a frontend/check-in y marcaba todos los entregables como completos. Esta versión corrige esa desviación. El estado verificable y las limitaciones de O1/O2 se encuentran en el [informe](../entregables/objetivos_1_2.md).

## Hitos y dependencias

| Hito | Fecha de las matrices / decisión | Dependencia y resultado |
|---|---|---|
| Base O1 | 19/09 o 26/09/2026 según versión; reconciliación pendiente | Cierre técnico con resultados de esta revisión; aceptación docente aparte |
| O2 | 01/10/2026 | O1 más baseline y refactor medidos; investigar niveles que incumplan metas |
| O3 | 15/10/2026 | O2 reproducible; caché opcional sin alterar la autoridad de PostgreSQL |
| O4 | 05/11/2026 | O3 validado; protocolo repetible y recuperación |
| Extensiones | Sin fecha comprometida | Aprobar necesidad y capacidad antes de UI, check-in, pagos o boletos |

El deadline 10/10 del Markdown anterior no se adopta silenciosamente. Las fechas son referencias académicas, no compromisos externos. El equipo debe resolver la discrepancia en la siguiente revisión con el docente.

## Definición de terminado

Una tarea técnica termina cuando tiene código/documento accesible, requisito trazado, comando reproducible, resultado real con alcance y revisión. Un script escrito sin ejecutar se marca “preparado”. Una meta incumplida se registra como fallo o limitación, aunque el reporte esté terminado. No se fabrican capturas, porcentajes ni actas de aceptación.

Cada PR debe incluir impacto, pruebas pertinentes y actualización de evidencia cuando cambien invariantes, contrato, esquema o comportamiento operativo. CI bloquea por estilo, pruebas, enlaces, migración y construcción. No publica ni despliega fuera del laboratorio automáticamente.

## Capacidad y organización

Los responsables son los de las matrices; la asignación operativa debe confirmarla el equipo. O1 y O2 requieren revisión cruzada de Backend/DBA y QA. Para O3 reservar inicialmente 3–5 jornadas de implementación y 2 de medición; O4 3 de escenarios, 2 de ejecución y 1 de informe. Son estimaciones, no fechas garantizadas. Mantener un 20% de margen para incidencias.

La infraestructura base utiliza Podman rootless, Compose, Alembic y GitHub Actions. Jenkins es una alternativa preparada que reutiliza Make. Vagrant solo añade valor si el equipo necesita una VM reproducible; no es necesario para ejecutar contenedores en este Linux. Ver [decisiones](../arquitectura/decisiones.md).

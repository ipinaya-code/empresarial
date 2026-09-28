# Evidencias que se deben presentar

La entrega O1/O2 consiste en el [informe técnico](../entregables/objetivos_1_2.md), este registro, el código y los archivos seleccionados en `docs/evidencias/`. Los resultados generados durante desarrollo viven en `artifacts/` y no se versionan automáticamente.

| Evidencia | Contenido mínimo | Criterio |
|---|---|---|
| E-01 | Metodología, objetivos y referencias | Explicar qué se observó y qué se supone |
| E-02 | ER y secuencia de reserva | Estados, transacción, rechazo y rollback |
| E-03 | JUnit PostgreSQL + log | Control negativo, ganador único, índice, expiración y lectura concurrente |
| E-04 | Diagrama baseline/refactor y prueba de contrato | Ambas versiones accesibles y mismo resultado |
| E-05 | JSON k6 por variante/nivel/repetición | p50/p95/p99, throughput, errores, checks y salida |
| E-06 | Reporte y gráfico derivados | Fuentes identificables; limitaciones y umbrales fallidos visibles |
| E-07 | Migración, imagen OCI y smoke | Entorno desplegable localmente; versión y comandos |
| E-08 | Playwright/JUnit | Navegador real; alcance explícito (API, todavía sin UI) |
| E-09 | Manifiesto de huellas | Artefactos + código/configuración, fecha y entorno |
| E-10 | Acta de revisión | Pendiente: autor/revisor/docente, fecha, observaciones y aceptación |

Para la exposición: comenzar por el problema y límites; mostrar control negativo aislado; presentar la protección y conteo SQL; recorrer la arquitectura; comparar resultados O2; explicar qué queda para O3/O4. No mostrar una pantalla verde como prueba de todos los requisitos.

La aceptación académica y la aceptación para producción son externas a esta ejecución. No se simulan firmas ni se marcan como realizadas. Revisar las evidencias cada vez que cambie el código o el escenario: una medición vale para su revisión y configuración concretas.

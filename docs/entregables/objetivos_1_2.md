# Informe de objetivos 1 y 2

Estudio de caso académico con datos sintéticos. La revisión conserva los objetivos de las matrices originales; no constituye una auditoría institucional ni aceptación docente.

## Objetivo 1: integridad transaccional

Se corrigió la discrepancia entre nombres de enum PostgreSQL y el predicado del índice de reservas activas. Se añadió unicidad de número de asiento por vuelo, una migración inicial y pruebas con transacciones independientes. La reserva provisional mantiene su estado en PostgreSQL; no depende de un lock distribuido en Valkey.

El control negativo usa una tabla aislada sin protecciones. Los flujos seguro/provisional conservan el índice y bloqueo por fila; se comprueba el ganador único, conflictos, número de reservas activas y estado del asiento. Las canceladas se conservan al expirar y permiten una nueva reserva.

## Objetivo 2: consultas y comparación

Baseline: materialización ORM del servicio previo del repositorio. Refactor: proyección de las columnas necesarias. Se mantiene el contrato JSON y se prueba que la lectura no espera el lock de una escritura. Ambas variantes se miden con caché desactivada; la caché pertenece a O3.

Los resultados de ejecución se incorporan al cerrar la verificación local. El criterio de aceptación y sus limitaciones están en el [protocolo](../testing/protocolo_pruebas_estres.md).

## Entrega y límites

El [registro de evidencias](../testing/evidencia_pruebas.md) define qué presentar. No se atribuyen tráfico, políticas, incidentes ni SLAs a BoA. La aceptación docente, el pipeline remoto y la habilitación de un servicio público son verificaciones distintas de esta entrega local.

La variante final refactorizada también declara `VueloDisponibilidadResponse` para validar y serializar con Pydantic. Baseline conserva la serialización genérica anterior. Por tanto, el tratamiento experimental combina proyección SQL y serialización tipada; no se atribuye todo el efecto a una sola técnica. Cambiar `READ_MODE` requiere reiniciar la API.

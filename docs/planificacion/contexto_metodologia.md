# Contexto, problema y metodología

## Planteamiento defendible

Se parte del relato del equipo acerca de dificultades de disponibilidad/reserva durante demanda elevada. No se aportaron registros de incidentes, entrevistas firmadas, analítica del portal, contratos ni información de producción. Por tanto, no es posible atribuir esas dificultades a una condición de carrera real de BoA ni cuantificar su frecuencia. El prototipo investiga una **hipótesis técnica** reproducible: consultas y escrituras concurrentes sin coordinación pueden producir asignaciones incompatibles.

Una observación de usuario (lentitud, error o disponibilidad que cambia) admite otras causas: agotamiento legítimo, red, pasarela, límites del proveedor o caché desactualizada. La sobreasignación técnica de un asiento tampoco equivale a la política comercial de sobreventa de pasajes. El laboratorio excluye la sobreventa comercial y no modela el inventario tarifario de una aerolínea completa.

## Pregunta y objetivos operativos

¿Puede un prototipo conservar como máximo una reserva activa por asiento bajo solicitudes simultáneas y responder consultas de disponibilidad mientras otra transacción modifica el inventario?

- H1: bloqueo por fila más unicidad parcial mantiene la invariante de asignación.
- H2: separar consultas de comandos y reducir la materialización de objetos conserva el contrato y permite medir cambios de latencia bajo la misma carga.
- H3 (objetivo 3): una caché opcional reduce lecturas SQL, con una política de frescura explícita.
- H4 (objetivo 4): un protocolo periódico detecta regresiones de capacidad y recuperación.

## Clasificación de afirmaciones

| Clase | Ejemplo | Respaldo requerido |
|---|---|---|
| Observación reportada | El equipo reporta dificultades en alta demanda | Ficha O-001; actualmente sin anexos de campo |
| Hecho del repositorio | Existe un índice único parcial | Migración, inspección SQL y prueba |
| Hipótesis | Una carrera podría explicar asignaciones incompatibles | Experimento reproducible; no extrapolar a BoA |
| Supuesto | 50/200/500 VU y pausa de 1 segundo | Protocolo y sensibilidad; no son tráfico real |
| Resultado | Latencia o conteo obtenido en una ejecución | Archivo bruto, configuración, fecha y huella de código |
| Referencia | NDC define intercambio de datos | Fuente primaria, fecha de consulta y alcance |

## Datos y diseño experimental

Doce vuelos sintéticos con 132 asientos cada uno y veinte pasajeros ficticios sirven como dataset de laboratorio. Rutas, horarios, configuración de cabina y prefijos no acreditan itinerarios, flota o políticas actuales de BoA. Las fechas del seed son relativas al momento de ejecución; registrar la respuesta del seed y mantener la misma base durante cada comparación. Usar dominios `example.test` y documentos ficticios; nunca importar datos personales de pasajeros.

Para H1, comparar un control negativo deliberadamente sin protecciones en una tabla aislada con las rutas protegidas. Mantener el índice de producción incluso en `/inseguro`: esa ruta demuestra ausencia de bloqueo, no garantiza duplicados persistidos. Para H2, conservar dataset, host, número de workers, pausa, duración, CPU/memoria y caché apagada; alternar el orden y repetir al menos tres veces por nivel. Publicar todas las ejecuciones, también las que fallen.

Variables dependientes: p50/p95/p99, req/s, errores, resultados de contratos y conteo SQL de reservas activas. Confusores: calentamiento, compilación, procesos del host, generador en la misma máquina, tamaño del pool, caché del SO/BD. No se infiere disponibilidad mensual de una prueba de segundos ni mejora porcentual a partir de un único máximo.

## Instrumentos para la investigación pendiente

Ficha O-001 (pendiente de completar por quien observó): fecha y zona horaria; canal y pasos; resultado esperado/observado; repetición; captura anonimizada si existe; condiciones de red; quién registró; permiso de uso. No completar retroactivamente campos desconocidos.

Guía de entrevista futura: cómo se reporta una reserva fallida; cómo se distingue un pago incierto de un asiento ocupado; volumen agregado de consultas/compras; reglas de expiración; objetivos de servicio; responsabilidad de incidentes. Se necesitarían acceso autorizado y consentimiento. El alcance actual no depende de obtenerlos.

Investigación documental pendiente: restricciones del proveedor PSS, licencias y esquemas IATA aplicables, protección de datos y requisitos sectoriales con asesoría competente, conservación de registros y continuidad institucional. No afirmar cumplimiento legal o certificación desde este prototipo.

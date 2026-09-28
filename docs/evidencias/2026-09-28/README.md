# Paquete de evidencia local

Datos sintéticos. Ejecución en Linux con Podman rootless. Fecha UTC de cierre en `manifest.json`; las primeras pruebas se iniciaron el 27/09 local y las últimas el 28/09. El commit base anterior a estos cambios es `5c4855f`; el árbol de trabajo contiene cambios sin commit, identificados por SHA-256.

- `preliminar/`: primera campaña completa (18 mediciones), proyección SQL con serialización genérica. Conserva sus fallos de umbral y el archivo de router que cambió después. Sus huellas de backend están en `environment.json`.
- `validacion/`: JUnit SQLite/PostgreSQL/Chromium, cobertura y verificaciones de esquema, migración y restauración.
- `final/`: campaña con proyección SQL y respuesta tipada; consultar resultados individuales y entorno.
- `manifest.json`: huellas de los artefactos revisados y de las fuentes actuales. No contiene secretos ni dumps.

La primera campaña no satisface los umbrales a 500 VU. Se conserva para justificar por qué se añadió serialización tipada y distinguir mediciones de afirmaciones. Las pruebas del navegador verifican API, no una UI de pasajeros aún inexistente.

Los XML conservan duración y resultado de cada test; el código muestra las aserciones de estado de la BD. Las imágenes SVG derivan de los JSON mediante `scripts/report_benchmark.py`, con Matplotlib 3.11.2. No se generaron datos para rellenar resultados.

Este paquete no acredita una ejecución remota de GitHub Actions, Jenkins ni un despliegue público. La aceptación docente está pendiente de revisión externa.

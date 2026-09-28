# Cómo regenerar los resultados

Desde la raíz, instalar herramientas con `make setup PYTHON=python3.12`. Arrancar una base PostgreSQL descartable llamada `boa_test` como indica el [README](../../README.md).

```bash
mkdir -p artifacts
make test-postgres > artifacts/postgres-test.log 2>&1
make compose-up
make seed
make browser-install
make test-browser
.venv/bin/python scripts/benchmark.py
```

No se usa el antiguo script que llamaba `/reset` y `/seed` inexistentes. La suite real está en `tests/postgres/test_integrity.py` y verifica también el estado de la base, no solo las respuestas HTTP. El log legible y el JUnit deben revisarse juntos.

Los diagramas Markdown son la fuente vigente. Los PNG históricos pueden tener rutas o conceptos anteriores; regenerarlos solo tras revisar su contenido. Ningún PNG se considera evidencia de una prueba ejecutada.

Después de las 18 ejecuciones, generar tabla y figura SVG con un entorno que tenga Matplotlib instalado:

```bash
python3 scripts/report_benchmark.py artifacts/benchmark
```

La figura de esta entrega se generó con Matplotlib 3.11.2 del host; no es una dependencia de ejecución de la API. Copiar los artefactos revisados a un directorio nuevo en `docs/evidencias/` y ejecutar `python3 scripts/evidence_manifest.py docs/evidencias/NOMBRE_DE_LA_CORRIDA`. El manifiesto excluye su propia huella e incluye archivos fuente y artefactos seleccionados.

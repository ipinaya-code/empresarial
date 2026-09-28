# Operación, despliegue y recuperación

## Entornos y ruta adoptada

Desarrollo: Python 3.12 y Podman rootless. Laboratorio integrado: Compose, PostgreSQL 15, Valkey opcional y API en loopback. CI: runner efímero con PostgreSQL real; sin publicación. Staging/producción: pendientes de proveedor, identidad, secretos, TLS y responsable operativo. No presentar el Compose local como alta disponibilidad.

Podman `compose` necesita un proveedor. Verificar `podman info`, `podman compose version` y `podman-compose --version`. Si la autodetección falla: `make compose-up COMPOSE=podman-compose`. Docker: `make compose-up CONTAINER_ENGINE=docker`. No se requiere socket Docker ni contenedores privilegiados.

## Arranque y actualización local

1. `make compose-up`; revisar `podman compose -f docker/docker-compose.yml ps`.
2. Esperar readiness con `curl --fail http://127.0.0.1:8000/api/v1/health/ready`.
3. `make seed` únicamente en laboratorio. Ejecutar smoke y revisar logs.
4. Antes de modificar esquema, respaldar. La migración corre una vez antes de lanzar workers en este Compose de una API. En despliegues con varias réplicas, usar un job único de migración.
5. `make compose-down` detiene y conserva volumen; no usar `down -v` si los datos deben conservarse.

La imagen se ejecuta con usuario no root. Imagen base y servicios tienen etiquetas de versión; registrar sus digests en cada entrega. Para una release institucional deberán fijarse digests, escanearse dependencias y firmarse artefactos.

## Bases anteriores a Alembic

La revisión 0001 crea el esquema desde cero. No debe aplicarse sobre tablas existentes ni usarse `stamp` para ocultar diferencias. Para datos desechables, crear un volumen nuevo conservando el anterior hasta verificar. Para datos necesarios: `pg_dump`, restaurar en laboratorio, comparar enums/índices/FK, detectar duplicados y redactar migración de adopción revisada. El índice anterior usaba estados incompatibles; corregirlo exige inspección de los datos. No hay migración automática de adopción en esta entrega.

## Backup y restauración de laboratorio

```bash
mkdir -p artifacts
podman compose -f docker/docker-compose.yml exec -T db \
  pg_dump -U boa_admin -d boa_reservas -Fc > artifacts/boa.dump
# Restaurar en otra base del contenedor, nunca sobre la fuente:
podman compose -f docker/docker-compose.yml exec -T db \
  createdb -U boa_admin boa_restore
podman compose -f docker/docker-compose.yml exec -T db \
  pg_restore -U boa_admin -d boa_restore --no-owner < artifacts/boa.dump
```

Adaptar usuario/base si se cambiaron valores. Verificar tablas, recuentos, índice parcial y versión Alembic en `boa_restore`. Medir tiempo; un archivo de backup sin restauración ensayada no demuestra recuperación. Cifrado, almacenamiento externo, retención y restauración programada quedan para staging. No copiar dumps de datos reales al repositorio.

## Rollback

Guardar referencia/digest de imagen anterior y backup antes de promover. Si falla solo código compatible, volver a la imagen anterior y comprobar readiness y smoke. Si falla esquema incompatible, detener escrituras y restaurar el backup en otra base, validar y redirigir; no ejecutar downgrade destructivo automáticamente. `alembic downgrade base` existe solo para probar reversibilidad de esquema vacío: elimina tablas.

## CI, Jenkins y promoción

GitHub Actions ejecuta estilo, enlaces, SQLite, PostgreSQL, migraciones, construcción y smoke de navegador. Archiva JUnit/cobertura/logs. El Jenkinsfile alternativo reutiliza Make en agente Linux con etiqueta `podman`; requiere instalar herramientas y disponer de PostgreSQL de pruebas. Su sintaxis/ejecución en servidor deberá validarse al provisionarlo.

Gate de staging público: identidad/autorización, idempotencia, TLS, secretos externos, rutas demo apagadas, límites de solicitudes, rol BD mínimo, restore probado, métricas/alertas, análisis de dependencias/imagen, presupuesto y responsable. Probar desde fuera que no se publican BD/Valkey ni administración. Solo después promover una imagen identificada por digest y ejecutar smoke. La aprobación debe referirse a un candidato concreto con sus resultados.

## Incidentes

BD caída: readiness 503, detener promoción, revisar conexión y recuperación; no habilitar un fallback de escritura. Valkey caído: lectura directa a BD, vigilar carga y recuperación; invalidar/reconstruir según política O3. Errores al migrar: conservar logs, no reintentar cambios destructivos a ciegas. Saturación: reducir carga, revisar CPU/pool/locks y comparar con último resultado; registrar causa y prueba de regresión.

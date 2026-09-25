# Evidencia de pruebas

Ejecutar con la API levantada:

```bash
python tests/test_concurrency.py
```

El resultado se guarda en `logs/concurrencia.log` e incluye:

- Número de solicitudes simultáneas.
- Respuestas HTTP exitosas y fallidas.
- Reservas activas persistidas en PostgreSQL.
- Sobreasignaciones persistidas.
- Estado final del asiento.

La prueba segura exige que exista exactamente una reserva activa y que el asiento termine en `CONFIRMADO`. La restricción única parcial de PostgreSQL protege también el caso en que una ruta omita accidentalmente el bloqueo.

Para validar el ciclo provisional manualmente:

```bash
curl -X POST http://localhost:8000/reservar/provisional -H "Content-Type: application/json" -d "{\"usuario_id\":1,\"asiento_id\":1}"
curl -X POST http://localhost:8000/reservar/1/confirmar
```

Si no se confirma antes de diez minutos, `POST /reservar/expirar` libera el asiento y marca la reserva como `CANCELADA`.

Para regenerar los diagramas:

```bash
python scripts/generar_diagrama.py
```

Las imágenes se guardan en `docs/diagramas/`.

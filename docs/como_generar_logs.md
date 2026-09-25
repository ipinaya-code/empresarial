# Cómo se generan los logs de concurrencia

## Objetivo

El archivo `logs/concurrencia.log` sirve como evidencia de la prueba de concurrencia del sistema de reservas. Registra y compara dos escenarios:

1. Reserva sin control transaccional.
2. Reserva con bloqueo pesimista mediante `SELECT FOR UPDATE`.

La prueba utiliza cinco solicitudes simultáneas que intentan reservar el mismo asiento.

## Archivos involucrados

- `tests/test_concurrency.py`: ejecuta la prueba y genera el log.
- `app/main.py`: contiene los endpoints `/reservar/inseguro` y `/reservar/seguro`.
- `app/models.py`: define reservas, estados e integridad de datos.
- `app/database.py`: conecta el test con PostgreSQL.
- `logs/concurrencia.log`: resultado persistido de la ejecución.

## Cómo se genera

### 1. Abrir PowerShell en la raíz

La raíz del proyecto es:

```powershell
cd "C:\Users\usser\Downloads\empresarial-main\empresarial-main\reserva_vuelos"
```

### 2. Iniciar Docker

Docker Desktop debe estar abierto y mostrar `Engine running`.

```powershell
docker compose -f docker/docker-compose.yml up -d --build
```

Este comando inicia:

- PostgreSQL en el puerto `5455`.
- La API FastAPI en el puerto `8000`.

Comprobar el estado:

```powershell
docker compose -f docker/docker-compose.yml ps
```

La base de datos debe aparecer como `healthy` y la API como `Up`.

### 3. Ejecutar la prueba

Desde la misma raíz del proyecto:

```powershell
Remove-Item logs\concurrencia.log -ErrorAction SilentlyContinue
python tests/test_concurrency.py
```

El primer comando elimina el log anterior para generar una evidencia limpia. El segundo ejecuta los dos escenarios.

La prueba segura tarda aproximadamente 60 segundos porque el endpoint seguro mantiene el bloqueo durante un minuto como parte de la simulación.

### 4. Consultar el archivo

```powershell
Get-Content logs\concurrencia.log
```

El archivo queda guardado en:

```text
logs/concurrencia.log
```

## Qué hace el script

Para cada escenario, `tests/test_concurrency.py` realiza estos pasos:

1. Llama a `POST /reset` para eliminar las reservas anteriores y liberar los asientos.
2. Llama a `POST /seed` para asegurar que existan vuelos, asientos y usuarios.
3. Obtiene el identificador del asiento de prueba.
4. Crea cinco solicitudes HTTP simultáneas.
5. Envía todas las solicitudes al mismo endpoint y al mismo asiento.
6. Mide el tiempo total de ejecución.
7. Cuenta las respuestas HTTP exitosas y fallidas.
8. Consulta PostgreSQL para contar las reservas activas realmente guardadas.
9. Calcula las sobreasignaciones persistidas.
10. Consulta el estado final del asiento.
11. Guarda todas esas evidencias en `logs/concurrencia.log`.

## Escenario sin control

Endpoint utilizado:

```text
POST /reservar/inseguro
```

Este endpoint consulta el asiento sin `SELECT FOR UPDATE`. Utiliza una espera corta de `0.5 segundos` para dejar visible la ventana de concurrencia.

El flujo es:

```text
Consultar asiento
    -> Verificar DISPONIBLE
    -> Esperar 0.5 segundos
    -> Confirmar asiento
    -> Crear reserva
```

Este escenario representa el flujo vulnerable a una condición de carrera. Además, el índice único de PostgreSQL sobre reservas activas actúa como protección adicional y puede rechazar solicitudes con HTTP `409`.

## Escenario con bloqueo

Endpoint utilizado:

```text
POST /reservar/seguro
```

Este endpoint consulta el asiento utilizando:

```sql
SELECT ... FOR UPDATE
```

El flujo es:

```text
Bloquear fila del asiento
    -> Verificar DISPONIBLE
    -> Mantener el bloqueo durante 60 segundos
    -> Confirmar asiento
    -> Crear reserva
    -> COMMIT
    -> Liberar bloqueo
```

Mientras la primera solicitud mantiene el bloqueo, las demás solicitudes esperan. Cuando el bloqueo se libera, encuentran el asiento en estado `CONFIRMADO` y reciben HTTP `400`.

## Significado de los datos del log

- `Solicitudes exitosas`: respuestas HTTP `200`.
- `Solicitudes fallidas`: respuestas diferentes de `200`.
- `Reservas activas persistidas`: reservas en estado `PENDIENTE` o `CONFIRMADA` guardadas en PostgreSQL.
- `Sobreasignaciones persistidas`: cantidad de reservas activas por encima de una para el mismo asiento.
- `Estado final del asiento`: estado almacenado en la tabla `asientos`.
- `HTTP 409`: conflicto por una reserva activa existente.
- `HTTP 400`: el asiento ya no está disponible.

## Resultado esperado

Un resultado correcto para el flujo seguro debe mostrar:

```text
Solicitudes exitosas: 1
Solicitudes fallidas: 4
Reservas activas persistidas: 1
Sobreasignaciones persistidas: 0
Estado final del asiento: confirmado
```

La diferencia principal entre ambos escenarios está en el mecanismo utilizado:

| Escenario | Mecanismo | Espera simulada | Resultado esperado |
|---|---|---:|---|
| Sin control | No usa bloqueo de fila | 0.5 segundos | Puede existir condición de carrera; la restricción de BD evita duplicados persistidos. |
| Con bloqueo | `SELECT FOR UPDATE` | 60 segundos | Solo una solicitud confirma el asiento y las demás son rechazadas. |

## Evidencia para presentar

El archivo que demuestra este requisito es:

```text
logs/concurrencia.log
```

Se puede presentar junto con:

- [Diagrama ER](diagrama_er.md)
- [Diagrama de secuencia](diagrama_secuencia_reserva.md)
- [Diagrama de flujo PNG](diagramas/diagrama_flujo_reserva_vuelos.png)

## Detener el entorno

Cuando termine la prueba:

```powershell
docker compose -f docker/docker-compose.yml down
```

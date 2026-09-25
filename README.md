# Prototipo transaccional de reserva de vuelos

## Responsable

**Iver Pinaya — Líder Backend / DBA**

## Descripción

Este proyecto implementa un prototipo de reserva de vuelos para demostrar cómo controlar la concurrencia al asignar asientos. El objetivo principal es evitar que dos o más usuarios confirmen el mismo asiento cuando existen solicitudes simultáneas.

El sistema utiliza una API REST desarrollada con FastAPI, SQLAlchemy como ORM y PostgreSQL como motor de base de datos. El flujo crítico incorpora bloqueo pesimista a nivel de fila mediante `SELECT FOR UPDATE`, transacciones y una reserva provisional temporal.

## Objetivos del trabajo

- Modelar la base de datos del proceso de reserva.
- Implementar usuarios, vuelos, asientos y reservas.
- Prevenir condiciones de carrera al asignar un asiento.
- Evitar la sobreescritura y duplicación de reservas activas.
- Implementar reservas provisionales con expiración.
- Confirmar o cancelar reservas según su vigencia.
- Comparar un flujo sin control transaccional con uno protegido.
- Registrar evidencia de las pruebas de concurrencia.
- Documentar el diseño mediante diagramas ER, de secuencia y de flujo.

## Estado de los entregables

Los puntos que estaban pendientes de respaldo ya fueron completados:

| Entregable                                    | Estado     | Respaldo                                                                                      |
| --------------------------------------------- | ---------- | --------------------------------------------------------------------------------------------- |
| DER del prototipo                             | Completado | `docs/diagramas/diagrama_er_reserva_vuelos.png` y `docs/diagrama_er.md`                       |
| Diagrama de secuencia con `SELECT FOR UPDATE` | Completado | `docs/diagramas/diagrama_secuencia_reserva_vuelos.png` y `docs/diagrama_secuencia_reserva.md` |
| Repositorio Git del módulo transaccional      | Completado | Commit `ff5d72a`                                                                              |
| Logs comparativos sin control vs. con bloqueo | Completado | `logs/concurrencia.log`, commit `a8e64e6`                                                     |

Por tanto, el proyecto cuenta con respaldo visual, técnico, documental y de ejecución para los cuatro puntos solicitados.

## Arquitectura

```text
Cliente HTTP
    |
    v
FastAPI
    |
    v
SQLAlchemy
    |
    v
PostgreSQL
```

### Tecnologías

- Python 3.11+
- FastAPI
- Uvicorn
- SQLAlchemy
- PostgreSQL 15
- psycopg2-binary
- Pydantic
- HTTPX
- Docker Compose o Podman Compose

## Estructura del proyecto

```text
reserva_vuelos/
├── app/
│   ├── database.py       # Conexión y sesiones de PostgreSQL
│   ├── main.py           # API y flujo transaccional
│   ├── models.py         # Modelos y restricciones de base de datos
│   └── schemas.py        # Validación de solicitudes y respuestas
├── docker/
│   ├── Dockerfile        # Imagen de la API
│   └── docker-compose.yml # PostgreSQL y API
├── docs/
│   ├── diagramas/
│   │   ├── diagrama_er_reserva_vuelos.png
│   │   ├── diagrama_flujo_reserva_vuelos.png
│   │   └── diagrama_secuencia_reserva_vuelos.png
│   ├── diagrama_er.md
│   ├── diagrama_secuencia_reserva.md
│   └── evidencia_pruebas.md
├── scripts/
│   └── generar_diagrama.py # Generador de los diagramas PNG
├── tests/
│   └── test_concurrency.py  # Prueba de solicitudes simultáneas
├── .dockerignore
├── .gitignore
├── Makefile
├── requirements.txt
└── README.md
```

## Modelo de datos

### Usuario

Representa a la persona que realiza una reserva.

- `id`: clave primaria.
- `nombre`: nombre del usuario.
- `email`: correo único.

### Vuelo

Representa el trayecto disponible.

- `id`: clave primaria.
- `origen`: aeropuerto o ciudad de origen.
- `destino`: aeropuerto o ciudad de destino.
- `fecha`: fecha y hora del vuelo.
- `capacidad`: cantidad declarada de asientos.

### Asiento

Representa un asiento perteneciente a un vuelo.

- `id`: clave primaria.
- `vuelo_id`: clave foránea hacia `vuelos`.
- `numero`: identificador del asiento, por ejemplo `1A`.
- `estado`: `DISPONIBLE`, `RESERVADO_PROVISIONAL` o `CONFIRMADO`.
- `fecha_expiracion`: fecha límite de una reserva provisional.

### Reserva

Relaciona un usuario con un asiento.

- `id`: clave primaria.
- `usuario_id`: clave foránea hacia `usuarios`.
- `asiento_id`: clave foránea hacia `asientos`.
- `fecha_reserva`: fecha de creación.
- `fecha_expiracion`: límite de la reserva provisional.
- `estado`: `PENDIENTE`, `CONFIRMADA` o `CANCELADA`.

La base de datos incluye un índice único parcial para impedir más de una reserva activa (`PENDIENTE` o `CONFIRMADA`) para el mismo asiento.

## Flujo transaccional

### Reserva segura

1. La API recibe `usuario_id` y `asiento_id`.
2. Valida que el usuario y el asiento existan.
3. Ejecuta una consulta con `SELECT FOR UPDATE`.
4. PostgreSQL bloquea la fila del asiento.
5. Se verifica que el asiento esté disponible.
6. Se simula un procesamiento de **1 minuto (60 segundos)** mientras la fila permanece bloqueada.
7. Se actualiza el asiento y se crea la reserva.
8. Se confirma la transacción con `COMMIT`.
9. Se libera el bloqueo.
10. Las demás solicitudes reciben un error porque el asiento ya no está disponible.

Mientras una solicitud mantiene el bloqueo, otra solicitud que intenta reservar el mismo asiento debe esperar hasta que termine la transacción. El minuto es una latencia simulada para hacer visible el efecto del bloqueo en la prueba.

El flujo inseguro utiliza una espera corta de **0.5 segundos** y no bloquea la fila antes de verificar el estado. Esa diferencia permite demostrar la condición de carrera.

### Reserva provisional

El flujo provisional separa la asignación del asiento de la confirmación final:

```text
DISPONIBLE
    |
    v
RESERVADO_PROVISIONAL
    |                 \
    |                  \ expira
    v                   v
CONFIRMADO        DISPONIBLE
```

La reserva provisional tiene una duración de diez minutos. Si se confirma dentro del plazo, el asiento pasa a `CONFIRMADO`. Si expira, la reserva pasa a `CANCELADA` y el asiento vuelve a `DISPONIBLE`.

## Endpoints

| Método | Ruta                               | Función                                                          |
| ------ | ---------------------------------- | ---------------------------------------------------------------- |
| `POST` | `/seed`                            | Crea un vuelo, 100 asientos y 10 usuarios de prueba.             |
| `POST` | `/reset`                           | Elimina reservas y libera los asientos para repetir las pruebas. |
| `POST` | `/reservar/inseguro`               | Flujo sin bloqueo pesimista, utilizado como comparación.         |
| `POST` | `/reservar/seguro`                 | Reserva confirmada con `SELECT FOR UPDATE`.                      |
| `POST` | `/reservar/provisional`            | Crea una reserva temporal pendiente.                             |
| `POST` | `/reservar/{reserva_id}/confirmar` | Confirma una reserva provisional vigente.                        |
| `POST` | `/reservar/expirar`                | Cancela reservas provisionales vencidas y libera asientos.       |

La documentación interactiva de FastAPI está disponible en `/docs` cuando la API está ejecutándose.

## Códigos HTTP principales

- `200`: operación completada.
- `400`: solicitud válida, pero el asiento no está disponible en el flujo directo.
- `404`: usuario, asiento o reserva inexistente.
- `409`: conflicto de concurrencia, reserva activa duplicada o reserva provisional expirada.
- `422`: datos de entrada inválidos.
- `500`: error interno inesperado, sin exponer detalles de la base de datos al cliente.

## Prueba de concurrencia

El archivo `tests/test_concurrency.py` ejecuta el siguiente escenario:

1. Reinicia los datos.
2. Inicializa el vuelo, los asientos y los usuarios.
3. Envía cinco solicitudes simultáneas para el mismo asiento.
4. Ejecuta el escenario inseguro.
5. Ejecuta el escenario seguro.
6. Consulta PostgreSQL después de las solicitudes.
7. Cuenta respuestas exitosas y fallidas.
8. Cuenta reservas activas realmente persistidas.
9. Calcula las sobreasignaciones persistidas.
10. Verifica que la ruta segura deje exactamente una reserva confirmada.

El resultado se guarda en:

```text
logs/concurrencia.log
```

La prueba utiliza cinco solicitudes como escenario simulado. Los volúmenes de tráfico y los datos de vuelos no representan estadísticas reales de BoA, ya que se calibran con valores estimados para demostrar el comportamiento transaccional.

## Diagramas

- [Diagrama ER en PNG](docs/diagramas/diagrama_er_reserva_vuelos.png)
- [Diagrama de flujo en PNG](docs/diagramas/diagrama_flujo_reserva_vuelos.png)
- [Diagrama de secuencia en PNG](docs/diagramas/diagrama_secuencia_reserva_vuelos.png)
- [Diagrama ER editable en Mermaid](docs/diagrama_er.md)
- [Diagrama de secuencia editable en Mermaid](docs/diagrama_secuencia_reserva.md)
- [Documentación de evidencia](docs/evidencia_pruebas.md)
- [Guía para generar los logs](docs/como_generar_logs.md)

## Ejecución con Docker

Desde la raíz del proyecto:

```bash
docker compose -f docker/docker-compose.yml up -d --build
```

Verificar los contenedores:

```bash
docker compose -f docker/docker-compose.yml ps
```

Abrir la API:

```text
http://localhost:8000/docs
```

Detener el entorno:

```bash
docker compose -f docker/docker-compose.yml down
```

El servicio PostgreSQL utiliza el puerto `5455` en el equipo local y el servicio API utiliza el puerto `8000`.

## Ejecución local

Crear el entorno e instalar dependencias:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Iniciar la API:

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

La variable `DATABASE_URL` puede configurarse para apuntar a PostgreSQL:

```text
postgresql://admin:admin@localhost:5455/reservas_db
```

## Comandos del Makefile

```bash
make setup       # Crea el entorno virtual e instala dependencias
make run         # Inicia la API
make test        # Ejecuta la prueba de concurrencia
make build       # Construye la imagen de la API
make compose-up  # Levanta PostgreSQL y la API
make compose-down
```

También se puede regenerar el material visual con:

```bash
python scripts/generar_diagrama.py
```

Las imágenes se guardan automáticamente en `docs/diagramas/`.

## Alcance y consideraciones

Este proyecto es un prototipo académico/técnico centrado en transaccionalidad y concurrencia. Los datos son simulados y no incluyen integración con sistemas reales de BoA, pagos, autenticación, emisión de boletos ni disponibilidad externa de vuelos.

Para un entorno productivo sería necesario agregar migraciones de base de datos, autenticación, autorización para operaciones administrativas, gestión de pagos, observabilidad, secretos seguros y políticas de cancelación más completas.

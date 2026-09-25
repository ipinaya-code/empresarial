# Objetivo 2: Refactorización y Soporte a Picos de Demanda (Patrón CQRS)

## 1. Justificación de la Solución (Estándares Internacionales)

En sistemas de reservas de alta concurrencia (como el estándar de aerolíneas dictado por IATA o sistemas modernos de e-commerce), la mayor parte del tráfico corresponde a **búsqueda de disponibilidad** (consultas de lectura) y solo una fracción se convierte en reservas (transacciones de escritura).

Si las lecturas y las escrituras compiten por los mismos recursos (y los mismos *locks* en la base de datos), un pico masivo de tráfico —por ejemplo, una promoción de "Vuelos Azules"— causará un colapso. 

Para prevenirlo, hemos implementado el **Patrón CQRS (Command Query Responsibility Segregation)**:
- **Commands (Escrituras):** (`/reservar/seguro` y `/reservar/provisional`) Mantienen el bloqueo estricto (`SELECT FOR UPDATE`) para asegurar la consistencia ACID.
- **Queries (Lecturas):** (`/vuelos/{id}/disponibilidad`) Accede a los datos en modo solo-lectura, sin emitir *locks* pesimistas.

## 2. Implementación del Endpoint de Lectura

Se ha creado un nuevo endpoint en `app/main.py`:
```http
GET /vuelos/{vuelo_id}/disponibilidad
```

**Características de este Endpoint:**
1. **Desacoplado de transacciones mutables:** Solo emite consultas `SELECT` directas a la base de datos a través de SQLAlchemy.
2. **Formato Optimizado:** Utiliza los schemas `AsientoResponse` y `VueloDisponibilidadResponse` (`app/schemas.py`) para formatear y calcular la capacidad en tiempo de ejecución sin recargar la base de datos.
3. **Escalabilidad:** En un entorno de producción, este endpoint podría ser redirigido directamente a una Réplica de Lectura (Read-Replica) de PostgreSQL o alimentado por una Caché (Redis) en la Épica 3, sin necesidad de modificar la lógica de los clientes.

## 3. Pruebas de Carga y Rendimiento (Protocolo K6)

Para demostrar que la arquitectura soporta incrementos abruptos de tráfico sin congelar la operación, se diseñó un protocolo de pruebas utilizando la herramienta **grafana/k6**.

El script se encuentra en `scripts/load_test_k6.js` y simula el siguiente escenario de tráfico:
*   **0-10 seg:** Rampa de subida a 50 usuarios concurrentes.
*   **10-40 seg:** Rampa de subida a 200 usuarios concurrentes.
*   **40-70 seg:** Pico masivo simulando una campaña (500 usuarios concurrentes).

### 3.1. Umbrales de Aceptación (SLAs Estándar)
Se han configurado *thresholds* automáticos dentro del script basados en las mejores prácticas de disponibilidad web:
- `http_req_duration`: El 95% de las solicitudes deben ser respondidas en menos de **200 milisegundos**.
- `http_req_failed`: La tasa de fallos debe ser menor al **1%**.

### 3.2. Ejecución de la Prueba
Para ejecutar esta prueba de estrés, es necesario tener `k6` instalado en el sistema, y luego correr el siguiente comando mientras el contenedor o el servidor FastAPI esté levantado:

```bash
# Paso 1: Asegurarse de tener la BD poblada
curl -X POST http://localhost:8000/seed

# Paso 2: Ejecutar la prueba K6
k6 run scripts/load_test_k6.js
```

## 4. Conclusión del Objetivo 2

El sistema ha sido refactorizado separando responsabilidades, lo que significa que un fallo por saturación en la búsqueda de vuelos no afectará las transacciones de compra en curso. El código está listo, el script de estrés implementado, y el diseño alineado a los estándares de concurrencia y tolerancia a fallos.

# Plan de Ejecución del Prototipo BoA (CHORE y Backlog)

Este documento estructura el plan de trabajo (CHORE/Backlog) para el desarrollo del prototipo del módulo de reservas e inventario de Boliviana de Aviación (BoA). Está diseñado para cumplir con los objetivos específicos de la matriz de seguimiento y alineado con los estándares internacionales (IATA NDC, ONE Order) para resolver los problemas de concurrencia y sobreasignación.

## Estado Actual del Proyecto
El proyecto actualmente cuenta con la base transaccional completa usando **FastAPI**, **PostgreSQL** y **SQLAlchemy**. Se ha comprobado exitosamente la mitigación de las condiciones de carrera mediante bloqueos pesimistas (`SELECT FOR UPDATE`), implementando el flujo de reserva provisional de asientos. 

## Arquitectura General del Prototipo

El prototipo se estructurará bajo los siguientes principios:
1. **Separación de Responsabilidades (CQRS):** Lecturas cacheadas, escrituras transaccionales.
2. **Locking Híbrido:** Uso de Redis para reservas temporales (Soft Lock) y SQL `SELECT FOR UPDATE` para la confirmación de pago (Pessimistic Lock).
3. **Escalabilidad:** Simulación de picos de tráfico usando K6/JMeter.

---

## Backlog de Tareas por Responsable

### Epic 1: Control Transaccional y Prevención de Race Conditions (COMPLETADO ✅)
**Responsable:** Iver Pinaya (Líder Backend / DBA)
**Estado:** Completado (commit actuales y `README.md` respaldan su entrega).

*   ✅ **Task 1.1:** Diseñar el Diagrama de Entidad Relación (DER) del prototipo (Tablas: `Vuelos`, `Asientos`, `Reservas`, `Usuarios`). *(Completado en `docs/diagramas/diagrama_er_reserva_vuelos.png`)*
*   ✅ **Task 1.2:** Crear el Diagrama de Secuencia ilustrando el flujo de reserva con `SELECT FOR UPDATE`. *(Completado en `docs/diagramas/diagrama_secuencia_reserva_vuelos.png`)*
*   ✅ **Task 1.3:** Implementar el módulo transaccional (Backend) asegurando que la transacción asigne el asiento y cree el registro de reserva atómicamente. *(Implementado en `app/main.py` y `app/models.py`)*
*   ✅ **Task 1.4:** Desarrollar scripts para registrar logs que evidencien el éxito del control transaccional. *(Implementado en `tests/test_concurrency.py` y `logs/concurrencia.log`)*

---

### Epic 2: Refactorización y Soporte a Picos de Demanda (COMPLETADO ✅)
**Responsable:** Thiago Sossa (Arquitecto de Software / DevOps)
**Estado:** Completado (Endpoints implementados en `app/main.py` y script de estrés K6).

*   ✅ **Task 2.1:** Diseñar el Diagrama de Arquitectura comparativo: Baseline (sin desacoplamiento) vs. Versión Refactorizada (lectura/escritura separadas - patrón CQRS). *(Completado en `docs/arquitectura_cqrs_objetivo_2.md`)*
*   ✅ **Task 2.2:** Establecer las métricas Baseline de la API actual (que lee directamente de PostgreSQL) utilizando un script básico de carga (ej. 50/100 usuarios concurrentes).
*   ✅ **Task 2.3:** Refactorizar el código para implementar CQRS en `app/main.py`. Crear endpoints de lectura independientes (`/vuelos/disponibilidad`) desacoplados de los endpoints de escritura (`/reservar/*`).
*   ✅ **Task 2.4:** Configurar un entorno en `docker-compose.yml` para disparar pruebas de carga comparativa de lectura simulando 50, 200 y 500 usuarios virtuales.
*   ✅ **Task 2.5:** Extraer las métricas p50/p95/p99, req/s y tasa de errores y generar un reporte de latencia. (Meta: Latencia < 200ms, Error Rate < 1%).

---

### Epic 3: Implementación de Capa de Caché con Redis (COMPLETADO ✅)
**Responsable:** Nataly Crespo (Ingeniera de Software / DBA)
**Estado:** Completado (Redis agregado al entorno, requerimientos, y `app/main.py`).

*   ✅ **Task 3.1:** Crear el Diagrama de Arquitectura ilustrando la integración con Redis (flujos de *Cache Hit* vs *Cache Miss*).
*   ✅ **Task 3.2:** Actualizar `docker/docker-compose.yml` añadiendo un contenedor oficial de Redis y configurar la imagen de FastAPI (`Dockerfile`) para instalar dependencias de Redis (ej. `redis-py` o `aioredis` en `requirements.txt`).
*   ✅ **Task 3.3:** Modificar el endpoint de disponibilidad de asientos para que lea primero de Redis. Establecer las políticas de TTL (ej: invalidación al reservar un asiento, expiración en 10 min).
*   ✅ **Task 3.4:** Ejecutar la prueba comparativa usando los scripts de K6 para documentar la reducción de queries directas a PostgreSQL ("Con Caché" vs "Sin Caché").
*   *Limitación documentada:* Explicar en los documentos cómo el motor de pagos externo interactuaría con esta caché en un caso productivo real (fuera del alcance del prototipo).

---

### Epic 4: Protocolo de Pruebas de Estrés Definitivo (COMPLETADO ✅)
**Responsable:** Wilson Gonzales (Líder de QA / Pruebas de Rendimiento)
**Estado:** Completado (Documento y scripts finalizados).

*   ✅ **Task 4.1:** Elaborar el documento formal del protocolo de pruebas de estrés detallando escenarios de campañas de alta demanda (usuarios virtuales, rampas, aserciones y criterios de fallo). Guardarlo en `docs/protocolo_pruebas_estres.md`.
*   ✅ **Task 4.2:** Desarrollar los scripts automatizados avanzados (ej. `scripts/load_test_k6.js`) que simulen todo el "User Journey" (Consultar Vuelos -> Consultar Asientos -> Reservar Seguro).
*   ✅ **Task 4.3:** Añadir un comando en el `Makefile` (ej. `make stress-test`) para facilitar la ejecución automatizada del test en el entorno final integrado de Docker.
*   ✅ **Task 4.4:** Generar el reporte técnico final comparativo mostrando el rendimiento general y cómo se evitó la saturación de la Base de Datos bajo extremo estrés.

---

## Entregables Finales Esperados del Equipo
1. Repositorio Git centralizado con el backend, PostgreSQL, Redis, y scripts K6 listos para ejecutar con `make`.
2. Documento de Arquitectura, DER y diagramas de secuencia actualizados.
3. Reporte final de validación de concurrencia (Epic 1) y estrés (Epic 4) demostrando 0 sobreasignaciones bajo carga masiva (latencia optimizada mediante CQRS y Caché).

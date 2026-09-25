# Protocolo de Pruebas de Estrés - Prototipo BoA

## 1. Objetivo General
Validar la capacidad, estabilidad y resistencia del nuevo módulo transaccional (basado en arquitectura CQRS, Caché de Redis y Postgres) bajo condiciones extremas de demanda, simulando escenarios reales de la aerolínea como la promoción "Vuelos Azules".

## 2. Escenarios y Rampas de Carga
El test simula un "User Journey" de búsqueda masiva, en donde miles de usuarios solicitan ver la disponibilidad de un vuelo simultáneamente.

| Etapa | Duración | Usuarios Virtuales (VU) | Comportamiento Simulado |
| :--- | :--- | :--- | :--- |
| **Warm-up (Calentamiento)** | 10 segundos | 50 VU | Ingreso paulatino de usuarios regulares. |
| **Escalamiento Medio** | 30 segundos | 200 VU | Primer impacto de notificación masiva. |
| **Pico de Estrés (Vuelos Azules)** | 30 segundos | 500 VU | Escenario crítico de altísima demanda y concurrencia. |
| **Cool-down (Enfriamiento)** | 10 segundos | 0 VU | Desconexión paulatina de los usuarios. |

## 3. Umbrales de Aceptación (SLAs - Service Level Agreements)

Basados en los estándares internacionales de disponibilidad de servicios IATA NDC y comercio electrónico, se establecen los siguientes umbrales (Thresholds):

1. **Latencia del 95% (p95):** Menor a **200 milisegundos**.
2. **Latencia del 99% (p99):** Menor a **500 milisegundos**.
3. **Tasa de Errores (Error Rate):** Menor al **1%** de todas las peticiones procesadas (Soporte > 99%).

## 4. Arquitectura Sometida a Prueba

*   **Lectura de Disponibilidad (`GET /vuelos/{id}/disponibilidad`):** Validará el comportamiento del patrón CQRS y el *Cache Hit Ratio* de Redis. 
*   **Aserciones (Checks):** 
    - Las peticiones retornan código HTTP 200.
    - La respuesta incluye el array de "asientos".
    - La capacidad retornada coincide con la base de datos (evitar lectura fantasma o de un caché corrupto).

## 5. Instrucciones de Ejecución

El protocolo se automatizó utilizando Grafana K6. 

### Pre-requisitos
1. `k6` debe estar instalado en la máquina anfitriona.
2. Contenedores de API, PostgreSQL y Redis deben estar operativos (`make compose-up`).
3. Ejecutar el seed (poblamiento de base de datos): `curl -X POST http://localhost:8000/seed`.

### Ejecución
Ejecutar el comando provisto en el `Makefile`:
```bash
make stress-test
```

### 6. Criterio de Fallo
El protocolo será calificado como "Fallido" si la herramienta de test K6 aborta con un código de salida distinto a cero por haber incumplido los umbrales (Ej. demasiadas peticiones fallaron, o la latencia promedio superó ampliamente los 200ms por saturación).

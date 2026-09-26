# 🛫 Plan Maestro — Sistema de Reservas BoA (Práctica Empresarial)

> **Proyecto:** Prototipo de Sistema de Reservas de Boliviana de Aviación (BoA)
> **Equipo:** Grupo 2 — Firefox
> **Fecha inicio:** 2026-09-26 | **Deadline Objetivo 3:** 2026-10-10
> **Repositorio:** [ipinaya-code/empresarial](https://github.com/ipinaya-code/empresarial)

---

## 📋 Visión General

Este proyecto simula un **sistema real de reservas aéreas** alineado con los estándares internacionales IATA (NDC, ONE Order), cubriendo el ciclo de vida completo de un pasajero: desde la búsqueda de vuelos hasta el boarding pass. Aunque es un prototipo educativo, debe reflejar la arquitectura, patrones y procesos que una aerolínea real implementaría en producción.

### Flujo Completo del Pasajero (Real)

```
Búsqueda de Vuelos → Selección de Asiento → Reserva Provisional (Soft Lock)
    → Datos del Pasajero → Pago (Simulado) → Confirmación (PNR)
    → Emisión de Boleto Electrónico (E-Ticket) → Check-in (Web/API)
    → Boarding Pass → Embarque
```

---

## 🎯 Los 4 Objetivos (Épicas)

### Estado Actual vs. Lo que Falta

| Objetivo | Épica | Estado | Responsable |
|----------|-------|--------|-------------|
| **Obj 1** | Control Transaccional y Prevención de Race Conditions | ✅ Completado | Iver Pinaya |
| **Obj 2** | Refactorización CQRS y Soporte a Picos de Demanda | ✅ Completado | Thiago Sossa |
| **Obj 3** | Ciclo de Vida Completo del Pasajero + Frontend + Infraestructura CI/CD | 🔄 **POR HACER** | Nataly Crespo + Equipo |
| **Obj 4** | Pruebas de Estrés Definitivas, Reportes y Documentación Final | 🔄 **POR HACER** | Wilson Gonzales + Equipo |

---

## 🏗️ OBJETIVO 1: Control Transaccional (COMPLETADO ✅)

**Responsable:** Iver Pinaya (Líder Backend / DBA)

### Tareas Completadas

| ID | Tarea | Evidencia | Criterio de Aceptación |
|----|-------|-----------|------------------------|
| T1.1 | Diagrama ER del prototipo | `docs/diagrama_er.md` + `docs/diagramas/diagrama_er_reserva_vuelos.png` | 4 tablas: Usuarios, Vuelos, Asientos, Reservas con relaciones FK |
| T1.2 | Diagrama de Secuencia `SELECT FOR UPDATE` | `docs/diagrama_secuencia_reserva.md` + `docs/diagramas/diagrama_secuencia_reserva_vuelos.png` | Muestra bloqueo, espera, commit/rollback |
| T1.3 | Módulo transaccional backend | `app/services/reserva_service.py` | Reserva atómica con `SELECT FOR UPDATE`, 3 flujos (inseguro, seguro, provisional) |
| T1.4 | Logs y evidencia de concurrencia | `tests/test_concurrency.py` + `logs/concurrencia.log` | 5 solicitudes simultáneas → 1 éxito, 4 rechazos, 0 sobreasignaciones |

### Entregables (Informe Obj. 1)
- [x] Documento de investigación IATA (`docs/investigacion_estandares_boa.md`)
- [x] Diagrama ER con campos IATA
- [x] Diagrama de secuencia con 3 flujos
- [x] Código fuente con tests unitarios
- [x] Log de evidencia de concurrencia

---

## 🏗️ OBJETIVO 2: Refactorización CQRS + Caché (COMPLETADO ✅)

**Responsable:** Thiago Sossa (Arquitecto de Software / DevOps)

### Tareas Completadas

| ID | Tarea | Evidencia | Criterio de Aceptación |
|----|-------|-----------|------------------------|
| T2.1 | Diagrama Arquitectura CQRS | `docs/arquitectura_cqrs_objetivo_2.md` | Baseline vs. Refactorizado, lecturas/escrituras separadas |
| T2.2 | Métricas Baseline (sin caché) | Script K6 + reporte | p95 < 200ms con 50 VU |
| T2.3 | Refactorización CQRS | `app/services/disponibilidad_service.py`, `app/api/v1/vuelos.py`, `app/api/v1/reservas.py` | Endpoints de lectura desacoplados de escritura |
| T2.4 | Integración Valkey (Caché) | `app/db/cache.py`, `docker/docker-compose.yml` | Cache Hit/Miss en disponibilidad, TTL 10min |
| T2.5 | Docker Compose completo | `docker/docker-compose.yml` | PostgreSQL + Valkey + API con healthchecks |
| T2.6 | Pipeline CI/CD GitHub Actions | `.github/workflows/ci.yml` | Lint (Ruff+Black) → Tests → Docker Build |

### Entregables (Informe Obj. 2)
- [x] Documento de arquitectura CQRS
- [x] Código refactorizado con servicios separados
- [x] Docker Compose con caché Valkey
- [x] CI/CD funcional en GitHub Actions
- [x] Evidencia de tests pasando (29/29, cobertura 77%)

---

## 🏗️ OBJETIVO 3: Ciclo de Vida Completo + Frontend + Infraestructura

> **Deadline:** 2026-10-10 (2 semanas)
> **Responsable principal:** Nataly Crespo + Todo el equipo

### 3.1 — Ampliación del Backend: Flujo Real de Aerolínea

| ID | Tarea | Descripción | Criterio de Aceptación | Responsable | Estimación |
|----|-------|-------------|------------------------|-------------|------------|
| T3.1 | **Endpoint de Check-in** | `POST /api/v1/checkin/{reserva_id}` — Permite al pasajero hacer check-in web 24h antes del vuelo. Cambia estado de reserva a `CHECKED_IN` y genera un boarding pass (JSON con datos del pasajero, vuelo, asiento, QR code simulado) | Reserva confirmada → checked_in, genera boarding pass con código QR (base64), rechaza si faltan >24h o si ya hizo check-in | Iver Pinaya | 2 días |
| T3.2 | **Modelo de Boleto Electrónico (E-Ticket)** | Nueva tabla `boletos` con número de boleto IATA (ej: `930-1234567890`), estado, fecha de emisión. Se genera automáticamente al confirmar la reserva | Tabla `boletos` con FK a reserva, número IATA válido, estado (`emitido`, `usado`, `cancelado`) | Nataly Crespo | 1 día |
| T3.3 | **Endpoint Itinerario del Pasajero** | `GET /api/v1/pasajero/{id}/itinerario` — Devuelve todas las reservas activas del pasajero con detalles de vuelo, asiento y boleto | JSON con lista de reservas, cada una con datos de vuelo, asiento, boleto y estado | Thiago Sossa | 1 día |
| T3.4 | **Endpoint de Cancelación de Reserva** | `POST /api/v1/reservar/{id}/cancelar` — Permite cancelar una reserva, liberando el asiento y registrando el motivo | Asiento vuelve a `disponible`, reserva pasa a `cancelada`, campo `motivo_cancelacion` | Iver Pinaya | 1 día |
| T3.5 | **Mejora del Seed: Horarios y Tarifas** | Agregar tabla `tarifas` con precios por clase (ejecutiva/económica) y horarios más realistas con múltiples frecuencias diarias | Tarifas BOB para ejecutiva (800-1200) y económica (300-600), mínimo 3 frecuencias diarias por ruta | Nataly Crespo | 1 día |

### 3.2 — Frontend Mínimo (Panel de Demostración)

| ID | Tarea | Descripción | Criterio de Aceptación | Responsable | Estimación |
|----|-------|-------------|------------------------|-------------|------------|
| T3.6 | **Panel Web: Búsqueda de Vuelos** | Página HTML/JS que consume `GET /api/v1/vuelos/{id}/disponibilidad` y muestra el mapa de asientos del Boeing 737-300 visualmente (18 ejecutiva + 114 económica) | Mapa de asientos interactivo con colores por estado (verde=disponible, amarillo=provisional, rojo=confirmado), información del vuelo | Wilson Gonzales | 2 días |
| T3.7 | **Panel Web: Flujo de Reserva** | Formulario para seleccionar asiento → ingresar datos → reservar provisional → confirmar. Consume los endpoints del backend | Flujo completo funcional desde el navegador, muestra PNR al confirmar, muestra errores si el asiento no está disponible | Wilson Gonzales | 2 días |
| T3.8 | **Panel Web: Check-in y Boarding Pass** | Página donde el pasajero ingresa su PNR, hace check-in y visualiza/descarga su boarding pass con código QR | Boarding pass visual con logo BoA simulado, datos del vuelo, asiento, hora, QR code | Wilson Gonzales | 1 día |

### 3.3 — Infraestructura CI/CD con Vagrant + Jenkins

| ID | Tarea | Descripción | Criterio de Aceptación | Responsable | Estimación |
|----|-------|-------------|------------------------|-------------|------------|
| T3.9 | **Vagrantfile: VM de Desarrollo** | Crear un `Vagrantfile` que provisione una VM Ubuntu con Docker, Docker Compose, Python 3.11, K6 y Jenkins preinstalados | `vagrant up` → VM funcional con todo instalado, acceso SSH, puertos mapeados (8000, 8080 Jenkins, 5455 PG) | Thiago Sossa | 1 día |
| T3.10 | **Jenkinsfile: Pipeline CI/CD** | Pipeline declarativo: Checkout → Lint → Test → Build Docker → Deploy (docker compose up) → Smoke Test | Pipeline ejecuta sin errores, muestra stages verdes, genera reportes de cobertura como artifacts | Thiago Sossa | 1 día |
| T3.11 | **Documentar Infraestructura** | Documento `docs/infraestructura_cicd.md` con diagramas de la VM, pipeline, puertos, y capturas de Jenkins ejecutando | Documento con diagrama Mermaid del pipeline, capturas del dashboard Jenkins, instrucciones de uso | Thiago Sossa | 0.5 días |

### 3.4 — Diagramas y Documentación Obj. 3

| ID | Tarea | Descripción | Formato |
|----|-------|-------------|---------|
| T3.12 | **Diagrama ER Extendido (v3)** | Agregar tablas `boletos` y `tarifas` al ER existente | Mermaid en `docs/diagrama_er.md` |
| T3.13 | **Diagrama de Secuencia: Check-in** | Flujo completo: PNR → validar → check-in → boarding pass | Mermaid en `docs/diagrama_secuencia_checkin.md` |
| T3.14 | **Diagrama de Secuencia: Cancelación** | Flujo: cancelar → liberar asiento → anular boleto | Mermaid en `docs/diagrama_secuencia_cancelacion.md` |
| T3.15 | **Diagrama C4 Actualizado** | Agregar Frontend como contenedor al diagrama C4 | Mermaid en `docs/arquitectura_sistema.md` |
| T3.16 | **Diagrama de Deployment con Vagrant** | VM → Docker Compose → Servicios | Mermaid en `docs/infraestructura_cicd.md` |

### Entregables del Informe Obj. 3
- [ ] Código fuente: endpoints check-in, cancelación, itinerario, boleto
- [ ] Frontend funcional con mapa de asientos y flujo de reserva
- [ ] Vagrantfile + Jenkinsfile funcionales
- [ ] 5 diagramas nuevos/actualizados
- [ ] Documento de infraestructura CI/CD
- [ ] Capturas de Jenkins ejecutando el pipeline
- [ ] Tests nuevos para endpoints nuevos (cobertura ≥ 80%)

---

## 🏗️ OBJETIVO 4: Pruebas de Estrés Definitivas + Reportes Finales

> **Deadline:** 2026-10-17 (1 semana después del Obj. 3)
> **Responsable principal:** Wilson Gonzales + Todo el equipo

### 4.1 — Pruebas de Estrés Avanzadas

| ID | Tarea | Descripción | Criterio de Aceptación | Responsable | Estimación |
|----|-------|-------------|------------------------|-------------|------------|
| T4.1 | **Script K6: User Journey Completo** | Simular el flujo completo: buscar → seleccionar → reservar → confirmar → check-in. Con 500 VU en pico | Script K6 con escenarios encadenados, métricas personalizadas por etapa | Wilson Gonzales | 2 días |
| T4.2 | **Script K6: Concurrencia Extrema** | 50 usuarios intentan reservar el MISMO asiento simultáneamente. Medir: exactamente 1 éxito, 49 rechazos, 0 sobreasignaciones | Threshold: 0 sobreasignaciones, latencia p99 < 2s bajo contención | Wilson Gonzales | 1 día |
| T4.3 | **Comparativa Con/Sin Caché** | Ejecutar misma carga con Valkey activo vs. desactivado. Documentar diferencia en latencia y throughput | Tabla comparativa con p50/p95/p99, req/s, cache hit ratio | Nataly Crespo | 1 día |
| T4.4 | **Reporte Técnico Final** | Documento con gráficas, tablas, conclusiones. Exportar resultados de K6 a JSON/CSV y generar visualizaciones | Reporte PDF/MD con mínimo 5 gráficas, análisis de resultados, recomendaciones | Wilson Gonzales | 2 días |

### 4.2 — Documentación Final

| ID | Tarea | Descripción | Criterio de Aceptación |
|----|-------|-------------|------------------------|
| T4.5 | **Manual de Usuario** | `docs/manual_usuario.md` — Cómo usar el sistema desde el frontend + API | Capturas de pantalla de cada pantalla, explicación paso a paso |
| T4.6 | **Manual Técnico** | `docs/manual_tecnico.md` — Arquitectura, instalación, configuración, deployment | Suficiente para que un desarrollador nuevo levante todo desde cero |
| T4.7 | **Informe Ejecutivo** | Resumen para stakeholders no técnicos: qué se logró, métricas clave, recomendaciones | 3-5 páginas, lenguaje accesible, gráficas resumen |
| T4.8 | **README Final** | Actualizar `README.md` con toda la documentación, badges, instrucciones completas | Readme profesional con badges de CI, cobertura, versión |

### Entregables del Informe Obj. 4
- [ ] Reportes de K6 con gráficas comparativas
- [ ] Log de evidencia de 0 sobreasignaciones bajo 500 VU
- [ ] Manual de usuario con capturas
- [ ] Manual técnico completo
- [ ] Informe ejecutivo
- [ ] README profesional final

---

## 📅 Cronograma Detallado (2 semanas hasta Obj. 3)

### Semana 1 (Sep 27 – Oct 3)

| Día | Lun 29 | Mar 30 | Mié 1 | Jue 2 | Vie 3 |
|-----|--------|--------|-------|-------|-------|
| **Iver** | T3.1 (Check-in backend) | T3.1 (finalizar + tests) | T3.4 (Cancelación) | T3.12 (ER v3) | Revisión + PR |
| **Nataly** | T3.2 (Modelo E-Ticket) | T3.5 (Tarifas + seed) | T3.5 (finalizar) | Tests para boletos | Revisión + PR |
| **Thiago** | T3.9 (Vagrantfile) | T3.10 (Jenkinsfile) | T3.11 (Doc infra) | T3.15 (C4 update) | Revisión + merge |
| **Wilson** | T3.6 (Frontend: mapa asientos) | T3.6 (finalizar mapa) | T3.7 (Flujo reserva) | T3.7 (finalizar) | Revisión + PR |

### Semana 2 (Oct 6 – Oct 10)

| Día | Lun 6 | Mar 7 | Mié 8 | Jue 9 | Vie 10 |
|-----|-------|-------|-------|-------|--------|
| **Iver** | T3.3 (Itinerario) | T3.13 (Seq check-in) | T3.14 (Seq cancelación) | Tests integración | **ENTREGA Obj. 3** |
| **Nataly** | Tests E-Ticket | T3.16 (Diag deployment) | Documentación | Revisión final | **ENTREGA Obj. 3** |
| **Thiago** | Deploy en Vagrant | Smoke tests Jenkins | Documentación | Revisión final | **ENTREGA Obj. 3** |
| **Wilson** | T3.8 (Check-in + boarding pass UI) | T3.8 (finalizar) | Integración frontend | Capturas evidencia | **ENTREGA Obj. 3** |

---

## 🗂️ Estructura Final del Proyecto (Post Obj. 3)

```
empresarial/
├── app/
│   ├── core/                  # Configuración, excepciones, logging
│   ├── models/                # Modelos SQLAlchemy (+ boleto, tarifa)
│   ├── schemas/               # Validación Pydantic
│   ├── services/              # Lógica de negocio (+ checkin, cancelación)
│   ├── api/v1/                # Routers FastAPI (+ checkin, itinerario)
│   ├── db/                    # Sesión BD + Caché Valkey
│   └── main.py                # App factory
├── frontend/                  # 🆕 Panel web de demostración
│   ├── index.html             # Búsqueda de vuelos
│   ├── reservar.html          # Flujo de reserva
│   ├── checkin.html           # Check-in + boarding pass
│   ├── css/                   # Estilos
│   └── js/                    # Lógica del frontend
├── tests/
│   ├── unit/                  # Tests unitarios
│   ├── integration/           # Tests con BD
│   └── e2e/                   # Tests de flujo completo
├── docker/
│   ├── Dockerfile             # Multi-stage build
│   └── docker-compose.yml     # PostgreSQL + Valkey + API
├── infrastructure/            # 🆕 Infraestructura como código
│   ├── Vagrantfile            # VM de desarrollo/producción simulada
│   └── Jenkinsfile            # Pipeline CI/CD
├── scripts/
│   └── load_test_k6.js        # Pruebas de carga K6
├── docs/                      # Documentación completa
│   ├── arquitectura_sistema.md
│   ├── diagrama_er.md
│   ├── diagrama_secuencia_reserva.md
│   ├── diagrama_secuencia_checkin.md     # 🆕
│   ├── diagrama_secuencia_cancelacion.md # 🆕
│   ├── infraestructura_cicd.md           # 🆕
│   ├── manual_usuario.md                 # 🆕 (Obj 4)
│   ├── manual_tecnico.md                 # 🆕 (Obj 4)
│   └── diagramas/
├── .github/workflows/ci.yml
├── pyproject.toml
├── Makefile
├── README.md
└── CHANGELOG.md
```

---

## 📊 Diagramas a Crear/Actualizar

| # | Diagrama | Archivo | Estado |
|---|----------|---------|--------|
| 1 | ER v1 (4 tablas) | `docs/diagrama_er.md` | ✅ Existe |
| 2 | Secuencia: Reserva Segura | `docs/diagrama_secuencia_reserva.md` | ✅ Existe |
| 3 | Secuencia: Reserva Provisional | `docs/diagrama_secuencia_reserva.md` | ✅ Existe |
| 4 | Secuencia: Flujo Inseguro | `docs/diagrama_secuencia_reserva.md` | ✅ Existe |
| 5 | Arquitectura C4 (Contexto) | `docs/arquitectura_sistema.md` | ✅ Existe |
| 6 | Arquitectura C4 (Contenedores) | `docs/arquitectura_sistema.md` | ✅ Existe |
| 7 | Flujo CQRS | `docs/arquitectura_sistema.md` | ✅ Existe |
| 8 | Deployment Docker | `docs/arquitectura_sistema.md` | ✅ Existe |
| 9 | **ER v3 (+ boletos, tarifas)** | `docs/diagrama_er.md` | 🆕 Obj 3 |
| 10 | **Secuencia: Check-in** | `docs/diagrama_secuencia_checkin.md` | 🆕 Obj 3 |
| 11 | **Secuencia: Cancelación** | `docs/diagrama_secuencia_cancelacion.md` | 🆕 Obj 3 |
| 12 | **C4 con Frontend** | `docs/arquitectura_sistema.md` | 🆕 Obj 3 |
| 13 | **Deployment Vagrant/Jenkins** | `docs/infraestructura_cicd.md` | 🆕 Obj 3 |
| 14 | **Diagrama de Estados del Asiento** | `docs/diagrama_estados.md` | 🆕 Obj 3 |
| 15 | **Diagrama de Estados de la Reserva** | `docs/diagrama_estados.md` | 🆕 Obj 3 |

---

## ✅ Criterios de Calidad Global

| Aspecto | Criterio | Herramienta |
|---------|----------|-------------|
| **Código** | Linting sin errores, formateo uniforme | Ruff + Black |
| **Tests** | Cobertura ≥ 80%, 0 tests fallidos | Pytest + pytest-cov |
| **CI/CD** | Pipeline verde en cada push | GitHub Actions + Jenkins |
| **Documentación** | Todos los diagramas actualizados, manuales completos | Mermaid + Markdown |
| **Concurrencia** | 0 sobreasignaciones bajo 500 VU | K6 + PostgreSQL FOR UPDATE |
| **Rendimiento** | p95 < 200ms, error rate < 1% | K6 thresholds |
| **Docker** | Imagen funcional, multi-stage, usuario no-root | Docker Build en CI |
| **Git** | Commits semánticos, branches por objetivo, PRs con template | Git + GitHub |

---

## 🔄 Convención de Branches

```
main                    ← rama estable (producción)
├── objetivo_2          ← Obj 1+2 completados (actual)
├── objetivo_3          ← 🆕 Obj 3: Check-in, Frontend, Vagrant
│   ├── feat/checkin-endpoint
│   ├── feat/eticket-model
│   ├── feat/frontend-seat-map
│   ├── feat/vagrant-jenkins
│   └── feat/cancellation
└── objetivo_4          ← 🆕 Obj 4: Estrés + Reportes finales
```

---

> [!IMPORTANT]
> **Próximo paso inmediato:** Crear la rama `objetivo_3`, empezar con T3.1 (endpoint check-in) y T3.2 (modelo E-Ticket) que son la base para todo lo demás. El frontend (T3.6-T3.8) depende de que estos endpoints estén listos.

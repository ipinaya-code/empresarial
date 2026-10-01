# Registro de decisiones de arquitectura

Estado: adoptadas para la base de laboratorio, 2026-09-27. Revisar ante un cambio de alcance.

| ADR | Decisión | Razón y consecuencia |
|---|---|---|
| 001 | Monolito modular; CQRS lógico | Facilita trazabilidad y operación del prototipo. No introducir broker ni Kubernetes sin una necesidad medida |
| 002 | PostgreSQL autoriza reservas | Lock por fila + índice parcial. SQLite solo contratos; sesiones PG independientes para concurrencia |
| 003 | TTL provisional persistido en BD | La pérdida de caché no pierde propiedad del asiento. Worker periódico aún pendiente |
| 004 | Caché apagada en O1/O2 | Aísla el experimento y mantiene O3 distinguible. Cache-aside preliminar requiere pruebas de frescura |
| 005 | Podman rootless + Compose | Aprovecha el entorno del usuario y una imagen OCI portable. Requiere proveedor Compose |
| 006 | Alembic antes de workers | Evita carreras de creación de tablas y permite seguimiento de esquema |
| 007 | GitHub Actions principal; Jenkins alternativo | Una sola interfaz Make. Jenkins necesita agente propio y no debe duplicar reglas o desplegar cada PR |
| 008 | Vagrant opcional, no prerrequisito | Añade aislamiento de SO si se necesita; consume RAM y requiere proveedor. Evaluarlo después de tener CI estable |
| 009 | Locks de dependencias con Python 3.12 | Instalaciones consistentes entre desarrollo, CI e imagen. Actualizar deliberadamente y volver a probar |
| 010 | Sin despliegue público de esta API | Falta identidad, autorización, rate limiting y operación institucional. El laboratorio sí es desplegable localmente |

Para reconsiderar Vagrant: comprobar virtualización, elegir libvirt u otro proveedor, fijar box y checksum, limitar puertos a loopback, provisionar Podman y ejecutar los mismos comandos Make. No instalar Jenkins dentro de cada VM de desarrollo; preferir agente separado. No se entrega un Vagrantfile no validado como si fuera infraestructura terminada.

Para adoptar Jenkins: agente Linux dedicado con Python 3.12, Podman rootless y proveedor Compose, aislamiento por workspace/build, credenciales en Jenkins y permisos mínimos. El Jenkinsfile realiza calidad y construcción; la promoción a staging necesita un entorno concreto y el gate de [operación](../operacion/despliegue.md).

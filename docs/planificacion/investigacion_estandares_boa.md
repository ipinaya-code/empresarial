# Referencias internacionales y aplicación al prototipo

Fuentes primarias consultadas el 27/09/2026. Se distingue el contenido de la referencia de la decisión del equipo. No se auditó ni certificó conformidad integral.

| Referencia | Qué sustenta | Aplicación / límite |
|---|---|---|
| [IATA NDC](https://www.iata.org/en/programs/airline-distribution/retailing/ndc/) | Intercambio de información de ofertas y órdenes; estándar basado en XML | Contexto del dominio. Esta API JSON propia no implementa los mensajes NDC |
| [IATA ONE Order](https://www.iata.org/en/programs/airline-distribution/retailing/one-order/) | Simplificación de registros de entrega y gestión de órdenes | Referencia para evolución de dominio; una tabla Reserva no acredita ONE Order |
| [PostgreSQL 15: bloqueo](https://www.postgresql.org/docs/15/explicit-locking.html) | Semántica de locks de fila y fin de transacción | `FOR UPDATE` en escrituras; lecturas MVCC sin bloqueo de fila |
| [PostgreSQL: índices parciales](https://www.postgresql.org/docs/15/indexes-partial.html) | Índices restringidos por predicado | Unicidad de reservas activas, conservando canceladas |
| [SQLAlchemy Enum](https://docs.sqlalchemy.org/en/20/core/type_basics.html#sqlalchemy.types.Enum) | Persistencia de nombres de miembros por defecto | Predicado SQL en mayúsculas, distinto del JSON |
| [ISO/IEC 25010:2023](https://www.iso.org/standard/78176.html) | Modelo de calidad de producto | Organizar requisitos de desempeño, fiabilidad, seguridad y mantenimiento |
| [ISO/IEC 27001:2022](https://www.iso.org/standard/27001) | Sistema de gestión de seguridad de información | Riesgos, responsables y evidencias; el repositorio no certifica una organización |
| [OWASP ASVS 5.0](https://github.com/OWASP/ASVS/tree/v5.0.0) | Requisitos verificables de seguridad de aplicaciones | Seleccionar controles de acceso, validación, configuración y registros antes de staging público |
| [WCAG 2.2](https://www.w3.org/TR/WCAG22/) | Accesibilidad del contenido web | Futura UI: teclado, foco, errores comprensibles y contraste; objetivo AA propuesto |

## Correcciones de la investigación previa

NDC no se usa como fuente para un SLA de 200 ms, una garantía de inventario durante diez minutos ni un mandato de Redis, CQRS o eventos. Estos son decisiones de implementación o metas experimentales. No se encontraron aquí fundamentos para afirmar que el caché reduzca 70% u 80% de consultas: el 70% es una meta de la matriz para O3 y requiere medición.

Una oferta comercial, una reserva temporal de inventario y un lock de base de datos tienen alcances diferentes. El prototipo mantiene la reserva temporal en PostgreSQL; Valkey no implementa soft locks distribuidos. Una consulta de disponibilidad puede envejecer entre lectura y compra; la escritura valida de nuevo.

`SKIP LOCKED` requiere una semántica de “cualquier recurso disponible”, no se aplica automáticamente a un asiento elegido. El proyecto conserva el lock sobre el asiento solicitado y rechaza el conflicto.

## Herramientas y fuentes de operación

- [Podman Compose](https://docs.podman.io/en/latest/markdown/podman-compose.1.html): delega en un proveedor externo; instalar y registrar su versión.
- [Playwright Python](https://playwright.dev/python/docs/intro): integración con pytest y navegadores; la suite actual verifica API desde Chromium.
- [k6 thresholds](https://grafana.com/docs/k6/latest/using-k6/thresholds/): los checks necesitan umbrales para afectar la salida del proceso.
- [Alembic](https://alembic.sqlalchemy.org/en/latest/tutorial.html): historial y ejecución de migraciones.
- [Jenkins Pipeline](https://www.jenkins.io/doc/book/pipeline/syntax/): pipeline declarativo; requiere un agente provisionado.
- [Vagrant providers](https://developer.hashicorp.com/vagrant/docs/providers): la VM depende del proveedor instalado; no sustituye Podman.

Las páginas públicas de ISO sustentan el ámbito general. Una evaluación cláusula por cláusula requeriría acceso legítimo al texto aplicable, alcance aprobado y personal competente. Requisitos legales bolivianos, pagos y relaciones con proveedores quedan como investigación institucional pendiente, sin conclusiones jurídicas en esta entrega.

[FastAPI: respuestas y serialización](https://fastapi.tiangolo.com/advanced/response-directly/) documenta el uso del modelo de respuesta con Pydantic. El objetivo 2 compara la ruta genérica anterior frente a un contrato tipado, además de reducir materialización ORM.

# Riesgos, asuntos abiertos y decisiones necesarias

| Riesgo | Probabilidad / impacto | Tratamiento y verificación | Responsable |
|---|---|---|---|
| Afirmar hechos institucionales sin datos | Alta / alto | Etiquetar observaciones e hipótesis; fuentes y revisión docente | Coordinación |
| Doble asignación | Media / crítico | Lock, índice y prueba PG; cero violaciones en cada ejecución | DBA |
| Resultado de SQLite interpretado como PG | Alta / alto | Suite PG obligatoria e independiente en CI | QA |
| Saturación de conexiones o CPU | Media / alto | Medir 50/200/500 VU y presupuesto de pools; no escalar a ciegas | DevOps |
| Caché obsoleta / carrera de invalidación | Alta / medio | Apagada por defecto; autoridad SQL; O3-02 | Backend |
| Abuso de IDs de reservas sin autenticación | Alta / crítico si se publica | Laboratorio loopback; bloquear publicación hasta control de acceso | Seguridad/Backend |
| Reset o seed contra datos reales | Media / crítico | Rutas solo desarrollo; suite en boa_test descartable | DBA |
| Migración sobre base preexistente | Media / alto | Respaldo, inspección y reconciliación; no stamp ciego | DBA |
| Resultados no reproducibles | Media / alto | Locks, comandos, huellas, repeticiones y ambiente registrado | QA |
| Caída y pérdida de datos | Media / alto | Restauración ensayada y políticas RPO/RTO antes de staging | DevOps |

## Decisiones pendientes con dueño y plazo relativo

1. Coordinación/docente, antes de aceptar O2: reconciliar las fechas de O1 y firmar alcance de objetivos. No depender de una aprobación ficticia.
2. Equipo autor, antes de distribución: confirmar derechos sobre contribuciones y materiales de terceros; se conserva la licencia MIT original del código. No usar correos corporativos sin respaldo.
3. DevOps, antes de staging: proveedor, región, dominio, presupuesto mensual, tamaño de VM, registro OCI y custodia de secretos. Propuesta inicial: una VM para demostración, BD persistente y proxy TLS, dimensionada a partir de mediciones; sin promesa de alta disponibilidad.
4. Backend, antes de usuarios externos: proveedor de identidad, permisos por reserva y tratamiento de reintentos de compra. Diseñar claves de idempotencia con respuesta persistida y conflicto de payload.
5. QA/negocio, antes de O4: distribución de carga, duración, capacidad mínima aceptable y ventana de frescura. 200 ms y 500 VU son metas propuestas, no contratos.
6. Operación, antes de publicar: RPO/RTO y retención. Propuesta de laboratorio: RPO ≤24 h, RTO ≤60 min, backups diarios y restauración mensual; medir y aprobar antes de convertir en compromiso.
7. Coordinación institucional, si se usa fuera del aula: permisos de marca, datos y sistemas, requisitos contractuales/sectoriales y responsables de tratamiento. Requiere investigación especializada.

Ninguna de estas decisiones impide ejecutar el laboratorio O1/O2. Sí condicionan la promoción a un servicio usado por terceros.

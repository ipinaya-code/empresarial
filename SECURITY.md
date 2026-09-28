# Seguridad y límites de uso

El servicio es un laboratorio académico sin autenticación de pasajeros. No publicar esta API directamente en Internet. Compose escucha en loopback; seed/reset/inseguro/expirar requieren `APP_ENV=development` y `DEMO_ROUTES_ENABLED=true`. Esta barrera reduce accidentes de laboratorio y no reemplaza autenticación o autorización.

Antes de exposición externa: verificar permisos por propietario de reserva, claves de idempotencia, límites de solicitudes, TLS, secretos, red privada de BD/caché, mínimo privilegio, tratamiento de errores, retención y anonimización de logs. Seleccionar y probar controles de OWASP ASVS con alcance documentado.

No usar pasajeros reales, tarjetas, credenciales corporativas ni logos que sugieran un servicio oficial. Las variables históricas `API_KEY`, `SECRET_KEY` y `RATE_LIMIT_PER_MINUTE` no implementan controles por sí solas.

Para informar una vulnerabilidad, usar un canal privado acordado con los mantenedores; no publicar credenciales ni detalles de explotación en un issue público. Todavía no hay canal institucional ni SLA de respuesta establecido. Revisar dependencias y la imagen antes de cada release; conservar el informe y resolver hallazgos según exposición e impacto.

# Investigación de Estándares Internacionales y Solución de Concurrencia para BoA

Este documento recopila la investigación técnica basada en estándares internacionales de la industria aeronáutica (IATA) y arquitecturas modernas de software para resolver los problemas de concurrencia (condiciones de carrera y sobreventa de asientos) en el sistema transaccional de Boliviana de Aviación (BoA).

## 1. Estándares Internacionales de la Industria (IATA)

La Asociación Internacional de Transporte Aéreo (IATA) ha impulsado transformaciones clave para modernizar los sistemas de reserva, dejando atrás los antiguos sistemas PSS (Passenger Service Systems) y los PNRs (Passenger Name Records).

### 1.1. IATA NDC (New Distribution Capability)
NDC es un estándar de transmisión de datos basado en XML/JSON que permite a las aerolíneas distribuir su contenido en tiempo real. 
- **Gestión de la Concurrencia a través de "Ofertas" (Offers):** El estándar NDC maneja la concurrencia mediante el concepto de *Offer Validity Windows* (Ventanas de Validez de Oferta). Cuando un usuario consulta disponibilidad, el sistema retorna una oferta con un tiempo de vida útil (TTL). Esto garantiza el precio y disponibilidad sin necesidad de bloquear la base de datos de inmediato.
- **Sincronización API:** Fomenta el uso de APIs síncronas que permiten a los clientes recuperar el estado más reciente, disminuyendo así las discrepancias de datos.

### 1.2. IATA ONE Order
ONE Order es la evolución del sistema de boletos. Centraliza todos los registros dispersos (PNR, E-ticket, EMD) en un único registro llamado **Order** (Pedido).
- **Manejo Centralizado de Estado:** Al utilizar un único registro, se simplifica el manejo de estados transaccionales. Un Order tiene estados bien definidos (Creado, Pagado, Confirmado, Entregado).
- **Arquitectura Basada en Eventos (Event-Driven):** ONE Order promueve que cualquier cambio en el estado del "Order" dispare eventos (Event-Driven Architecture). Esto permite que los sistemas de inventario, pago y facturación se mantengan sincronizados en tiempo real sin saturar la base de datos relacional principal con bloqueos (locks) innecesarios.

## 2. Patrones Arquitectónicos para la Asignación de Asientos (Mitigación de Race Conditions)

El problema de la sobreasignación ocurre por un "Race Condition" o condición de carrera, donde dos usuarios intentan reservar el mismo asiento al mismo tiempo. Los estándares de la industria tecnológica aplican las siguientes estrategias:

### 2.1. Bloqueos Temporales Distribuidos (Soft Locks)
Es el estándar más usado en comercio electrónico de alta escala.
- **Herramienta:** Redis o Memcached.
- **Funcionamiento:** Cuando el Usuario A selecciona el asiento 12B, el sistema escribe en la memoria caché (Redis) un registro llave-valor con un Tiempo de Vida (TTL) de, por ejemplo, 10 minutos. Durante este tiempo, si el Usuario B consulta el mismo asiento, la caché indicará que está temporalmente reservado.
- **Ventaja:** No bloquea la base de datos principal, permitiendo soportar ráfagas de tráfico masivas.

### 2.2. Bloqueo Pesimista (Pessimistic Locking) a nivel de Base de Datos
Garantiza consistencia estricta en el motor de base de datos.
- **Implementación (SQL):** Se utiliza la instrucción `SELECT ... FOR UPDATE`.
- **Evolución (`SKIP LOCKED`):** Motores como PostgreSQL o MySQL 8.0 soportan `FOR UPDATE SKIP LOCKED`. Si varios usuarios piden "cualquier asiento en clase económica", la base de datos asigna automáticamente el siguiente disponible sin hacer que las transacciones hagan fila esperando a que se libere el asiento anterior.

### 2.3. Patrón CQRS (Command Query Responsibility Segregation)
Recomendado para campañas de alta demanda (ej. Vuelos Azules).
- **Separación de Lectura y Escritura:** Las consultas de disponibilidad (Read) se dirigen a una base de datos replicada o a una capa de caché en memoria (Redis). Las transacciones de compra/reserva (Write) van a la base de datos transaccional principal.
- **Beneficio:** Evita que las miles de consultas por minuto "congelen" el motor principal, permitiendo que las reservas sigan fluyendo.

## 3. Conclusión y Alineación con el Prototipo de BoA

Para el prototipo de BoA, la combinación de estos conceptos internacionales se traduce en:

1. **Gestión de Estado Centralizada (Inspirado en ONE Order):** Las tablas del prototipo deben reflejar un modelo unificado de "Reserva/Orden".
2. **Caché para Consultas (CQRS y Redis):** Reducir la carga de lectura en un 80% usando Redis para entregar los itinerarios y la disponibilidad inicial.
3. **Mecanismo de Lock Transaccional Híbrido:**
   - *Soft Lock (Redis):* Reserva temporal del asiento (10 minutos) mientras el usuario está en el checkout.
   - *Hard Lock (FOR UPDATE):* Solo al momento de confirmar el pago y escribir en la base de datos se usa un bloqueo transaccional fugaz para garantizar ACID.
4. **Pruebas de Estrés:** Usar herramientas como K6 para verificar que, simulando 500+ usuarios concurrentes pidiendo el mismo asiento, solo 1 obtenga éxito y los 499 restantes sean rechazados sin corromper la BD ni degradar la latencia (<= 200ms).

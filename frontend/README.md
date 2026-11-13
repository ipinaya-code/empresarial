# Frontend — BoA Reservas (prototipo)

Interfaz de pasajeros para la API FastAPI del repositorio.

Stack: React 19 + Vite + TypeScript, Tailwind CSS v4 y [HeroUI v3](https://heroui.com).

## Arranque

Requisitos: Node.js 20+ y la API levantada en `http://127.0.0.1:8000` con datos de prueba (`make compose-up && make seed` desde la raíz).

```bash
cd frontend
npm install
npm run dev        # http://localhost:3000
```

El servidor de desarrollo reenvía `/api` al backend (proxy de Vite), así que no hace falta tocar CORS. Para otro destino, copiar `.env.example` a `.env` y ajustar `API_PROXY_TARGET`.

## Comandos

| Comando | Uso |
|---|---|
| `npm run dev` | Servidor de desarrollo en el puerto 3000 |
| `npm run build` | Verificación de tipos y build de producción en `dist/` |
| `npm run lint` | Lint con oxlint |
| `npm run preview` | Sirve el build de producción |

## Flujo implementado

1. Consultar un vuelo por ID (`GET /api/v1/vuelos/{id}/disponibilidad`).
2. Mapa de asientos coloreado por estado y clase.
3. Reserva provisional de 10 minutos con contador (`POST /api/v1/reservar/provisional`).
4. Confirmación y código de reserva (`POST /api/v1/reservar/{id}/confirmar`).

Los errores de la API (`{"detail": ...}`, p. ej. 409 si el asiento ya fue tomado) se muestran como alerta.

## Estructura

```text
src/
  api/          cliente HTTP y tipos de la API
  components/   FlightSearch, FlightCard, SeatMap, ReservationPanel
  hooks/        useCountdown
  App.tsx       estado y orquestación del flujo
```

## Pendiente en el backend

La API no expone aún listado/búsqueda de vuelos, registro/login ni consulta/cancelación de reservas del pasajero; por eso los IDs de vuelo y pasajero se ingresan manualmente.

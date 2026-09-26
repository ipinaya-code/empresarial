/**
 * Prueba de Carga K6 — Sistema de Reservas BoA
 *
 * Simula el escenario de alta demanda "Vuelos Azules" donde
 * cientos de usuarios concurrentes consultan disponibilidad
 * y realizan reservas simultáneamente.
 *
 * Ejecutar: k6 run scripts/load_test_k6.js
 * Prerrequisito: make compose-up && make seed
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Counter, Rate, Trend } from 'k6/metrics';

// ── Métricas personalizadas ──────────────────────────────────
const cacheHits = new Counter('cache_hits');
const reservaExitos = new Counter('reserva_exitos');
const reservaFallos = new Counter('reserva_fallos');
const disponibilidadDuration = new Trend('disponibilidad_duration', true);

// ── Configuración de la prueba ───────────────────────────────
export const options = {
  stages: [
    { duration: '10s', target: 50 },   // Warm-up: 50 VU
    { duration: '30s', target: 200 },  // Escalamiento: 200 VU
    { duration: '30s', target: 500 },  // Pico "Vuelos Azules": 500 VU
    { duration: '10s', target: 0 },    // Cool-down
  ],
  thresholds: {
    // SLAs basados en estándares IATA NDC
    http_req_duration: ['p(95)<200', 'p(99)<500'],
    http_req_failed: ['rate<0.01'],
    disponibilidad_duration: ['p(95)<150'],
  },
};

const BASE_URL = __ENV.API_URL || 'http://localhost:8000';

// ── Escenario principal: User Journey ────────────────────────
export default function () {
  // 1. Consultar disponibilidad (CQRS: Lectura)
  const dispRes = http.get(`${BASE_URL}/api/v1/vuelos/1/disponibilidad`);
  disponibilidadDuration.add(dispRes.timings.duration);

  check(dispRes, {
    'disponibilidad: HTTP 200': (r) => r.status === 200,
    'disponibilidad: contiene asientos': (r) => {
      const body = r.json();
      return body.asientos !== undefined;
    },
    'disponibilidad: capacidad correcta': (r) => {
      const body = r.json();
      return body.capacidad_total === 132;  // Boeing 737-300
    },
    'disponibilidad: tiene código IATA': (r) => {
      const body = r.json();
      return body.codigo !== undefined && body.codigo.startsWith('OB-');
    },
  });

  // Pausa entre iteraciones (simula lectura del pasajero)
  sleep(Math.random() * 2 + 0.5);
}

// ── Escenario de escritura: Reserva bajo carga ───────────────
export function reservaConcurrente() {
  const usuarioId = Math.floor(Math.random() * 20) + 1;
  const asientoId = Math.floor(Math.random() * 132) + 1;

  const payload = JSON.stringify({
    usuario_id: usuarioId,
    asiento_id: asientoId,
  });

  const headers = { 'Content-Type': 'application/json' };
  const res = http.post(`${BASE_URL}/api/v1/reservar/seguro`, payload, { headers });

  if (res.status === 200) {
    reservaExitos.add(1);
  } else {
    reservaFallos.add(1);
  }

  check(res, {
    'reserva: respuesta válida': (r) => [200, 400, 409].includes(r.status),
    'reserva: sin error 500': (r) => r.status !== 500,
  });

  sleep(1);
}

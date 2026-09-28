// Objetivo 2: lecturas idénticas contra baseline/refactored SIN caché.
// Los umbrales son metas del laboratorio, no SLAs de IATA o BoA.
import http from 'k6/http';
import { check, sleep } from 'k6';
export const options = {
  vus: Number(__ENV.VUS || 50),
  duration: __ENV.DURATION || '15s',
  summaryTrendStats: ['avg', 'med', 'p(95)', 'p(99)', 'max'],
  thresholds: {
    http_req_duration: ['p(95)<200', 'p(99)<500'],
    http_req_failed: ['rate<0.01'],
    checks: ['rate==1'],
  },
};
const url = `${__ENV.API_URL || 'http://127.0.0.1:8000'}/api/v1/vuelos/${__ENV.VUELO_ID || 1}/disponibilidad`;
export default function () {
  const res = http.get(url, { timeout: '10s' });
  let body = {};
  try { body = res.json(); } catch (_) { /* check informa JSON inválido */ }
  check(res, {
    'HTTP 200': (r) => r.status === 200,
    'contrato de inventario': () => Array.isArray(body.asientos) && body.asientos.length === body.capacidad_total,
    'disponibilidad acotada': () => body.asientos_disponibles >= 0 && body.asientos_disponibles <= body.capacidad_total,
  });
  sleep(1);
}

export function handleSummary(data) {
  return { stdout: JSON.stringify(data, null, 2) + '\n' };
}

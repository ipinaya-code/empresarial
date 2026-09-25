import http from 'k6/http';
import { check, sleep } from 'k6';

// Configuración de la prueba de carga
export const options = {
  stages: [
    { duration: '10s', target: 50 },  // Rampa de subida a 50 usuarios virtuales (VU)
    { duration: '30s', target: 200 }, // Rampa a 200 VU
    { duration: '30s', target: 500 }, // Pico de 500 VU (Simulando "Vuelos Azules")
    { duration: '10s', target: 0 },   // Rampa de bajada
  ],
  thresholds: {
    // Definimos criterios de aceptación basados en industria
    http_req_duration: ['p(95)<200', 'p(99)<500'], // El 95% de las peticiones debe ser < 200ms
    http_req_failed: ['rate<0.01'],                // La tasa de error debe ser menor al 1%
  },
};

export default function () {
  // Asumimos que el vuelo de prueba (seed) tiene ID 1
  const url = 'http://localhost:8000/vuelos/1/disponibilidad';
  
  // Realizar la consulta GET (Lectura - CQRS)
  const res = http.get(url);

  // Validaciones
  check(res, {
    'estado es 200': (r) => r.status === 200,
    'respuesta contiene asientos': (r) => r.json().asientos !== undefined,
    'capacidad devuelta es 100': (r) => r.json().capacidad_total === 100,
  });

  // Pausa corta entre iteraciones de un usuario
  sleep(1);
}

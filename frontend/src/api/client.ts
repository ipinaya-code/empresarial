import type { Reserva, VueloDisponibilidad } from './types'

const API_URL = (import.meta.env.VITE_API_URL as string | undefined) ?? '/api/v1'

export class ApiError extends Error {
  readonly status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response
  try {
    response = await fetch(`${API_URL}${path}`, {
      ...init,
      headers: { 'Content-Type': 'application/json', ...init?.headers },
    })
  } catch {
    throw new ApiError(0, 'No se pudo conectar con la API. ¿Está levantado el backend?')
  }
  const body = await response.json().catch(() => null)
  if (!response.ok) {
    const detail = body?.detail
    const message = typeof detail === 'string' ? detail : `Error ${response.status}`
    throw new ApiError(response.status, message)
  }
  return body as T
}

export function obtenerDisponibilidad(vueloId: number) {
  return request<VueloDisponibilidad>(`/vuelos/${vueloId}/disponibilidad`)
}

export function reservarProvisional(usuarioId: number, asientoId: number) {
  return request<Reserva>('/reservar/provisional', {
    method: 'POST',
    body: JSON.stringify({ usuario_id: usuarioId, asiento_id: asientoId }),
  })
}

export function confirmarReserva(reservaId: number) {
  return request<Reserva>(`/reservar/${reservaId}/confirmar`, { method: 'POST' })
}

/** El backend devuelve fechas UTC sin zona horaria. */
export function parseFechaApi(fecha: string): Date {
  return new Date(/[zZ]|[+-]\d{2}:\d{2}$/.test(fecha) ? fecha : `${fecha}Z`)
}

export type EstadoAsiento = 'disponible' | 'reservado_provisional' | 'confirmado' | 'bloqueado'
export type ClaseServicio = 'ejecutiva' | 'economica'
export type EstadoReserva = 'pendiente' | 'confirmada' | 'cancelada'

export interface Asiento {
  id: number
  numero: string
  fila: number
  columna: string
  clase: ClaseServicio
  estado: EstadoAsiento
}

export interface VueloDisponibilidad {
  vuelo_id: number
  codigo: string
  origen_iata: string
  origen_nombre: string
  destino_iata: string
  destino_nombre: string
  aeronave: string
  fecha_salida: string
  capacidad_total: number
  asientos_disponibles: number
  asientos_ejecutiva_disponibles: number
  asientos_economica_disponibles: number
  asientos: Asiento[]
}

export interface Reserva {
  id: number
  codigo_reserva: string
  usuario_id: number
  asiento_id: number
  estado: EstadoReserva
  fecha_reserva: string
  fecha_expiracion: string | null
}

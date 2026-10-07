import { Card, Chip } from '@heroui/react'
import { parseFechaApi } from '../api/client'
import type { VueloDisponibilidad } from '../api/types'

export function FlightCard({ vuelo }: { vuelo: VueloDisponibilidad }) {
  const salida = parseFechaApi(vuelo.fecha_salida).toLocaleString('es-BO', {
    dateStyle: 'full',
    timeStyle: 'short',
    timeZone: 'UTC',
  })

  return (
    <Card>
      <Card.Header>
        <Card.Description>
          Vuelo {vuelo.codigo} · {vuelo.aeronave}
        </Card.Description>
        <Card.Title className="text-2xl">
          {vuelo.origen_iata} → {vuelo.destino_iata}
        </Card.Title>
        <Card.Description>
          {vuelo.origen_nombre} → {vuelo.destino_nombre}
        </Card.Description>
      </Card.Header>
      <Card.Content className="flex flex-col gap-3">
        <p className="text-sm first-letter:uppercase">Salida: {salida}</p>
        <div className="flex flex-wrap gap-2">
          <Chip color="accent">
            {vuelo.asientos_disponibles}/{vuelo.capacidad_total} disponibles
          </Chip>
          <Chip>Ejecutiva: {vuelo.asientos_ejecutiva_disponibles}</Chip>
          <Chip>Económica: {vuelo.asientos_economica_disponibles}</Chip>
        </div>
      </Card.Content>
    </Card>
  )
}

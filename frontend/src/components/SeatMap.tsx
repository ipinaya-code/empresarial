import { Card } from '@heroui/react'
import type { Asiento, EstadoAsiento } from '../api/types'

const ESTILO_ESTADO: Record<EstadoAsiento, string> = {
  disponible: 'bg-success/20 text-foreground hover:bg-success/40 cursor-pointer',
  reservado_provisional: 'bg-warning/60 text-foreground cursor-not-allowed',
  confirmado: 'bg-surface-tertiary text-muted line-through cursor-not-allowed',
  bloqueado: 'bg-danger/30 text-muted cursor-not-allowed',
}

const LEYENDA: [EstadoAsiento, string][] = [
  ['disponible', 'Disponible'],
  ['reservado_provisional', 'Reserva provisional'],
  ['confirmado', 'Confirmado'],
  ['bloqueado', 'Bloqueado'],
]

interface Props {
  asientos: Asiento[]
  seleccionado: Asiento | null
  onSelect: (asiento: Asiento) => void
}

export function SeatMap({ asientos, seleccionado, onSelect }: Props) {
  const columnas = [...new Set(asientos.map((a) => a.columna))].sort()
  const mitad = Math.ceil(columnas.length / 2)
  const filas = new Map<number, Map<string, Asiento>>()
  for (const asiento of asientos) {
    if (!filas.has(asiento.fila)) filas.set(asiento.fila, new Map())
    filas.get(asiento.fila)!.set(asiento.columna, asiento)
  }
  const numerosFila = [...filas.keys()].sort((a, b) => a - b)

  const celda = (asiento: Asiento | undefined, key: string) => {
    if (!asiento) return <div key={key} className="size-9" />
    const activo = seleccionado?.id === asiento.id
    return (
      <button
        key={key}
        type="button"
        data-testid={`asiento-${asiento.numero}`}
        aria-label={`Asiento ${asiento.numero}, ${asiento.clase}, ${asiento.estado.replace('_', ' ')}`}
        aria-pressed={activo}
        title={`${asiento.numero} · ${asiento.clase}`}
        disabled={asiento.estado !== 'disponible'}
        onClick={() => onSelect(asiento)}
        className={`size-9 rounded-md text-xs font-medium transition-colors ${ESTILO_ESTADO[asiento.estado]} ${
          activo ? 'bg-accent! text-accent-foreground! ring-2 ring-accent ring-offset-2' : ''
        }`}
      >
        {asiento.numero}
      </button>
    )
  }

  return (
    <Card>
      <Card.Header>
        <Card.Title>Mapa de asientos</Card.Title>
        <Card.Description>Selecciona un asiento disponible.</Card.Description>
      </Card.Header>
      <Card.Content className="flex flex-col gap-4">
        <div className="flex flex-wrap gap-3 text-xs">
          {LEYENDA.map(([estado, texto]) => (
            <span key={estado} className="flex items-center gap-1.5">
              <span className={`inline-block size-3 rounded-sm ${ESTILO_ESTADO[estado].split(' ')[0]}`} />
              {texto}
            </span>
          ))}
        </div>
        <div className="flex max-h-[32rem] flex-col items-center gap-1 overflow-y-auto py-2">
          {numerosFila.map((fila) => {
            const asientosFila = filas.get(fila)!
            const ejecutiva = [...asientosFila.values()][0]?.clase === 'ejecutiva'
            return (
              <div key={fila} className="flex items-center gap-1">
                <span className="w-6 text-right text-xs text-muted">{fila}</span>
                {columnas.slice(0, mitad).map((c) => celda(asientosFila.get(c), c))}
                <span className="w-6" />
                {columnas.slice(mitad).map((c) => celda(asientosFila.get(c), c))}
                <span className="w-6 text-[10px] text-accent">{ejecutiva ? 'EJ' : ''}</span>
              </div>
            )
          })}
        </div>
      </Card.Content>
    </Card>
  )
}

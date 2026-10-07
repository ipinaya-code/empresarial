import { Alert, Button, Card, Label, ProgressBar } from '@heroui/react'
import { parseFechaApi } from '../api/client'
import type { Asiento, Reserva } from '../api/types'
import { useCountdown } from '../hooks/useCountdown'

interface Props {
  asiento: Asiento | null
  reserva: Reserva | null
  pending: boolean
  onReservar: () => void
  onConfirmar: () => void
  onNueva: () => void
}

function formatear(segundos: number) {
  const m = Math.floor(segundos / 60)
  const s = segundos % 60
  return `${m}:${s.toString().padStart(2, '0')}`
}

export function ReservationPanel({ asiento, reserva, pending, onReservar, onConfirmar, onNueva }: Props) {
  const expiracion = reserva?.estado === 'pendiente' && reserva.fecha_expiracion ? parseFechaApi(reserva.fecha_expiracion) : null
  const restante = useCountdown(expiracion)
  const total = expiracion && reserva ? Math.max(1, (expiracion.getTime() - parseFechaApi(reserva.fecha_reserva).getTime()) / 1000) : 1

  if (reserva?.estado === 'confirmada') {
    return (
      <Card>
        <Card.Content className="flex flex-col gap-4">
          <Alert status="success">
            <Alert.Indicator />
            <Alert.Content>
              <Alert.Title>Reserva confirmada</Alert.Title>
              <Alert.Description>
                Código de reserva: <strong data-testid="codigo-reserva">{reserva.codigo_reserva}</strong>
              </Alert.Description>
            </Alert.Content>
          </Alert>
          <Button variant="secondary" onPress={onNueva}>
            Nueva reserva
          </Button>
        </Card.Content>
      </Card>
    )
  }

  if (reserva?.estado === 'pendiente') {
    const expirada = restante === 0
    return (
      <Card>
        <Card.Header>
          <Card.Title>Reserva provisional</Card.Title>
          <Card.Description>
            Asiento {asiento?.numero} · Código {reserva.codigo_reserva}
          </Card.Description>
        </Card.Header>
        <Card.Content className="flex flex-col gap-4">
          <ProgressBar value={restante} maxValue={total} color={restante < 60 ? 'danger' : 'accent'}>
            <Label>Tiempo para confirmar</Label>
            <span className="text-sm font-medium tabular-nums">{formatear(restante)}</span>
            <ProgressBar.Track>
              <ProgressBar.Fill />
            </ProgressBar.Track>
          </ProgressBar>
          {expirada && (
            <Alert status="warning">
              <Alert.Indicator />
              <Alert.Content>
                <Alert.Title>La reserva expiró</Alert.Title>
                <Alert.Description>Elige otro asiento o inténtalo de nuevo.</Alert.Description>
              </Alert.Content>
            </Alert>
          )}
          <div className="flex gap-2">
            <Button onPress={onConfirmar} isPending={pending} isDisabled={expirada}>
              Confirmar reserva
            </Button>
            <Button variant="ghost" onPress={onNueva}>
              Cancelar
            </Button>
          </div>
        </Card.Content>
      </Card>
    )
  }

  return (
    <Card>
      <Card.Header>
        <Card.Title>Tu reserva</Card.Title>
        <Card.Description>
          {asiento
            ? `Asiento ${asiento.numero} (${asiento.clase === 'ejecutiva' ? 'Ejecutiva' : 'Económica'})`
            : 'Aún no seleccionaste un asiento.'}
        </Card.Description>
      </Card.Header>
      <Card.Content>
        <p className="text-sm text-muted">
          Se aparta el asiento por 10 minutos (reserva provisional). Debes confirmar antes de que termine el tiempo.
        </p>
      </Card.Content>
      <Card.Footer>
        <Button fullWidth onPress={onReservar} isPending={pending} isDisabled={!asiento}>
          Reservar asiento
        </Button>
      </Card.Footer>
    </Card>
  )
}

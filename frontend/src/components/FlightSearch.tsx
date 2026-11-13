import { Button, Card, Label, NumberField } from '@heroui/react'

interface Props {
  vueloId: number
  usuarioId: number
  loading: boolean
  onVueloIdChange: (value: number) => void
  onUsuarioIdChange: (value: number) => void
  onSearch: () => void
}

export function FlightSearch({ vueloId, usuarioId, loading, onVueloIdChange, onUsuarioIdChange, onSearch }: Props) {
  return (
    <Card>
      <Card.Header>
        <Card.Title>Buscar vuelo</Card.Title>
        <Card.Description>
          La API aún no lista vuelos ni tiene login: ingresa el ID del vuelo (1–12 con datos de prueba) y del
          pasajero (1–20).
        </Card.Description>
      </Card.Header>
      <Card.Content>
        <div className="flex flex-wrap items-end gap-4">
        <NumberField value={vueloId} minValue={1} onChange={onVueloIdChange} className="w-40">
          <Label>ID de vuelo</Label>
          <NumberField.Group>
            <NumberField.DecrementButton />
            <NumberField.Input />
            <NumberField.IncrementButton />
          </NumberField.Group>
        </NumberField>
        <NumberField value={usuarioId} minValue={1} onChange={onUsuarioIdChange} className="w-40">
          <Label>ID de pasajero</Label>
          <NumberField.Group>
            <NumberField.DecrementButton />
            <NumberField.Input />
            <NumberField.IncrementButton />
          </NumberField.Group>
        </NumberField>
        <Button onPress={onSearch} isPending={loading} isDisabled={!vueloId}>
          Consultar disponibilidad
        </Button>
        </div>
      </Card.Content>
    </Card>
  )
}

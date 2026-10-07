import { Alert, Spinner } from '@heroui/react'
import { useCallback, useEffect, useState } from 'react'
import { confirmarReserva, obtenerDisponibilidad, reservarProvisional } from './api/client'
import type { Asiento, Reserva, VueloDisponibilidad } from './api/types'
import { FlightCard } from './components/FlightCard'
import { FlightSearch } from './components/FlightSearch'
import { ReservationPanel } from './components/ReservationPanel'
import { SeatMap } from './components/SeatMap'

export default function App() {
  const [vueloId, setVueloId] = useState(1)
  const [usuarioId, setUsuarioId] = useState(1)
  const [vuelo, setVuelo] = useState<VueloDisponibilidad | null>(null)
  const [asiento, setAsiento] = useState<Asiento | null>(null)
  const [reserva, setReserva] = useState<Reserva | null>(null)
  const [loading, setLoading] = useState(true)
  const [pending, setPending] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const refrescarVuelo = useCallback(async (id: number) => {
    try {
      setVuelo(await obtenerDisponibilidad(id))
    } catch {
      // Se conserva el mapa anterior; el error principal ya se mostró.
    }
  }, [])

  const cargarVuelo = useCallback(async (id: number) => {
    setLoading(true)
    setError(null)
    try {
      setVuelo(await obtenerDisponibilidad(id))
    } catch (e) {
      setVuelo(null)
      setError((e as Error).message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    obtenerDisponibilidad(1)
      .then(setVuelo)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  const buscar = () => {
    setAsiento(null)
    setReserva(null)
    void cargarVuelo(vueloId)
  }

  const reservar = async () => {
    if (!asiento) return
    setPending(true)
    setError(null)
    try {
      setReserva(await reservarProvisional(usuarioId, asiento.id))
    } catch (e) {
      setError((e as Error).message)
      setAsiento(null)
    } finally {
      setPending(false)
      if (vuelo) void refrescarVuelo(vuelo.vuelo_id)
    }
  }

  const confirmar = async () => {
    if (!reserva) return
    setPending(true)
    setError(null)
    try {
      setReserva(await confirmarReserva(reserva.id))
    } catch (e) {
      setError((e as Error).message)
      setReserva(null)
      setAsiento(null)
    } finally {
      setPending(false)
      if (vuelo) void refrescarVuelo(vuelo.vuelo_id)
    }
  }

  const nueva = () => {
    setReserva(null)
    setAsiento(null)
    setError(null)
  }

  return (
    <div className="min-h-screen bg-background">
      <header className="bg-accent text-accent-foreground">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <h1 className="text-xl font-semibold">BoA Reservas</h1>
          <span className="text-xs opacity-80">Prototipo académico · datos sintéticos</span>
        </div>
      </header>

      <main className="mx-auto flex max-w-6xl flex-col gap-6 px-6 py-8">
        <FlightSearch
          vueloId={vueloId}
          usuarioId={usuarioId}
          loading={loading}
          onVueloIdChange={setVueloId}
          onUsuarioIdChange={setUsuarioId}
          onSearch={buscar}
        />

        {error && (
          <Alert status="danger">
            <Alert.Indicator />
            <Alert.Content>
              <Alert.Title>No se pudo completar la operación</Alert.Title>
              <Alert.Description>{error}</Alert.Description>
            </Alert.Content>
          </Alert>
        )}

        {loading && !vuelo && (
          <div className="flex justify-center py-12">
            <Spinner size="lg" />
          </div>
        )}

        {vuelo && (
          <div className="grid gap-6 lg:grid-cols-[1fr_22rem]">
            <SeatMap
              asientos={vuelo.asientos}
              seleccionado={asiento}
              onSelect={(a) => !reserva && setAsiento(a)}
            />
            <div className="flex flex-col gap-6">
              <FlightCard vuelo={vuelo} />
              <ReservationPanel
                asiento={asiento}
                reserva={reserva}
                pending={pending}
                onReservar={reservar}
                onConfirmar={confirmar}
                onNueva={nueva}
              />
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

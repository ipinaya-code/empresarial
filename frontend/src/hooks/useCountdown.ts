import { useEffect, useState } from 'react'

export function useCountdown(target: Date | null): number {
  const [now, setNow] = useState(() => Date.now())

  useEffect(() => {
    if (!target) return
    const id = window.setInterval(() => setNow(Date.now()), 1000)
    return () => window.clearInterval(id)
  }, [target])

  if (!target) return 0
  return Math.max(0, Math.floor((target.getTime() - now) / 1000))
}

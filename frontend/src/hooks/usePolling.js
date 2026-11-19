import { useCallback, useEffect, useRef, useState } from 'react'

export function usePolling(callback, interval = 2500, enabled = true) {
  const savedCallback = useRef(callback)
  useEffect(() => {
    savedCallback.current = callback
  }, [callback])

  const [tick, setTick] = useState(0)
  const refresh = useCallback(() => setTick((value) => value + 1), [])

  useEffect(() => {
    if (!enabled) return undefined
    let cancelled = false
    const run = async () => {
      try {
        await savedCallback.current()
      } catch (_) {
        /* polling errors are handled by the caller */
      }
    }
    run()
    const id = setInterval(() => {
      if (!cancelled) run()
    }, interval)
    return () => {
      cancelled = true
      clearInterval(id)
    }
  }, [interval, enabled, tick])

  return refresh
}

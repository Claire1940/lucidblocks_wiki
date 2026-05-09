'use client'

import { useEffect, useRef } from 'react'

export function PopunderAd({ adUrl }: { adUrl: string }) {
  const loaded = useRef(false)

  useEffect(() => {
    if (!adUrl || adUrl === '0' || loaded.current) return

    const script = document.createElement('script')
    script.async = true
    script.setAttribute('data-cfasync', 'false')
    script.src = adUrl
    document.body.appendChild(script)
    loaded.current = true

    return () => {
      if (script.parentNode) {
        script.parentNode.removeChild(script)
      }
      loaded.current = false
    }
  }, [adUrl])

  return null
}

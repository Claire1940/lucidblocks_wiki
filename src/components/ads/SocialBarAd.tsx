'use client'

import { useEffect, useRef } from 'react'

interface SocialBarAdProps {
  adKey: string
}

/**
 * 社交栏广告组件
 * 浮动式社交分享栏
 */
export function SocialBarAd({ adKey }: SocialBarAdProps) {
  const scriptLoadedRef = useRef(false)

  useEffect(() => {
    if (!adKey || adKey === '0' || scriptLoadedRef.current) return

    const script = document.createElement('script')
    script.src = `https://pl28666057.effectivegatecpm.com/${adKey}.js`
    document.body.appendChild(script)
    scriptLoadedRef.current = true

    return () => {
      if (script.parentNode) {
        script.parentNode.removeChild(script)
      }
      scriptLoadedRef.current = false
    }
  }, [adKey])

  return null
}

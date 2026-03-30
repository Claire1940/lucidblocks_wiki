'use client'

import { useEffect, useRef } from 'react'

interface IframeBannerAdProps {
  adKey: string
  width: number
  height: number
  className?: string
}

/**
 * iframe 横幅广告组件
 * 使用 Adsterra 的 atOptions 配置方式
 */
export function IframeBannerAd({ adKey, width, height, className = '' }: IframeBannerAdProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const scriptLoadedRef = useRef(false)

  useEffect(() => {
    if (!adKey || scriptLoadedRef.current || !containerRef.current) return

    const container = containerRef.current

    // 创建 atOptions 配置脚本
    const configScript = document.createElement('script')
    configScript.type = 'text/javascript'
    configScript.text = `
      atOptions = {
        'key' : '${adKey}',
        'format' : 'iframe',
        'height' : ${height},
        'width' : ${width},
        'params' : {}
      };
    `

    // 创建广告加载脚本
    const adScript = document.createElement('script')
    adScript.type = 'text/javascript'
    adScript.src = `https://www.highperformanceformat.com/${adKey}/invoke.js`

    // 按顺序添加脚本
    container.appendChild(configScript)
    container.appendChild(adScript)
    scriptLoadedRef.current = true

    return () => {
      if (configScript.parentNode) {
        configScript.parentNode.removeChild(configScript)
      }
      if (adScript.parentNode) {
        adScript.parentNode.removeChild(adScript)
      }
      scriptLoadedRef.current = false
    }
  }, [adKey, width, height])

  if (!adKey) return null

  return (
    <div className={`w-full flex justify-center ${className}`}>
      <div
        ref={containerRef}
        style={{
          maxWidth: '100%',
          width: `${width}px`,
          height: `${height}px`,
        }}
      />
    </div>
  )
}

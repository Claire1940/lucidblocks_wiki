'use client'

import { useEffect, useRef } from 'react'

interface AdBannerProps {
  /**
   * 广告类型
   */
  type: 'banner-300x250' | 'banner-468x60' | 'banner-728x90' | 'banner-160x600' | 'banner-320x50'
  className?: string
  /**
   * 广告 key（可选）
   * 如果提供且为空，则不渲染广告
   */
  adKey?: string
}

const AD_CONFIGS = {
  'banner-300x250': {
    width: 300,
    height: 250,
  },
  'banner-468x60': {
    width: 468,
    height: 60,
  },
  'banner-728x90': {
    width: 728,
    height: 90,
  },
  'banner-160x600': {
    width: 160,
    height: 600,
  },
  'banner-320x50': {
    width: 320,
    height: 50,
  },
}

// 广告加载超时时间（毫秒）
const AD_LOAD_TIMEOUT_MS = 8000

// 全局队列类型定义
interface HighPerformanceWindow extends Window {
  __highPerformanceAdQueue?: Promise<void>
  atOptions?: {
    key: string
    format: string
    height: number
    width: number
    params: Record<string, unknown>
  }
}

/**
 * 队列化广告加载任务
 * 防止多个广告同时加载导致冲突
 */
function enqueueHighPerformanceAdLoad(task: () => Promise<void>) {
  const w = window as HighPerformanceWindow
  const queue = w.__highPerformanceAdQueue ?? Promise.resolve()
  const next = queue.then(task, task)
  w.__highPerformanceAdQueue = next.then(
    () => undefined,
    () => undefined,
  )
  return next
}

/**
 * 横幅广告组件（动态脚本加载）
 * 使用 Adsterra 横幅广告
 * 队列化加载，防止并发冲突
 */
export function AdBanner({ type, className = '', adKey }: AdBannerProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const scriptLoadedRef = useRef(false)

  useEffect(() => {
    if (!adKey || adKey === '0' || scriptLoadedRef.current || !containerRef.current) {
      return
    }

    const container = containerRef.current
    const config = AD_CONFIGS[type]

    // 队列化加载广告
    enqueueHighPerformanceAdLoad(async () => {
      return new Promise<void>((resolve, reject) => {
        const timeoutId = setTimeout(() => {
          console.warn(`[AdBanner] Load timeout for ${type}`)
          reject(new Error('Ad load timeout'))
        }, AD_LOAD_TIMEOUT_MS)

        try {
          const w = window as HighPerformanceWindow
          w.atOptions = {
            key: adKey,
            format: 'iframe',
            height: config.height,
            width: config.width,
            params: {},
          }

          const invokeScript = document.createElement('script')
          invokeScript.type = 'text/javascript'
          invokeScript.src = `https://www.highperformanceformat.com/${adKey}/invoke.js`
          invokeScript.async = true

          invokeScript.onload = () => {
            clearTimeout(timeoutId)
            console.log(`[AdBanner] Loaded: ${type}`)
            resolve()
          }

          invokeScript.onerror = (error) => {
            clearTimeout(timeoutId)
            console.error(`[AdBanner] Failed to load: ${type}`, error)
            reject(error)
          }

          container.appendChild(invokeScript)
        } catch (error) {
          clearTimeout(timeoutId)
          reject(error)
        }
      })
    })

    scriptLoadedRef.current = true

    return () => {
      // 清理脚本
      const scripts = container.querySelectorAll('script')
      scripts.forEach((script) => {
        if (script.parentNode) {
          script.parentNode.removeChild(script)
        }
      })
      scriptLoadedRef.current = false
    }
  }, [adKey, type])

  // 如果 adKey 未配置或为空，不渲染
  if (!adKey || adKey === '0') {
    return null
  }

  const config = AD_CONFIGS[type]

  return (
    <div className={`flex justify-center ${className}`}>
      <div
        ref={containerRef}
        style={{
          maxWidth: `${config.width}px`,
          width: '100%',
          minHeight: `${config.height}px`,
        }}
      />
    </div>
  )
}

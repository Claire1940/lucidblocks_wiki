'use client'

interface SidebarAdProps {
  /**
   * 广告类型
   * sidebar-160x600: 左侧竖幅广告
   * sidebar-160x300: 右侧方形广告
   */
  type: 'sidebar-160x600' | 'sidebar-160x300'
  className?: string
  /**
   * 广告 key（可选）
   * 如果提供且为空，则不渲染广告
   */
  adKey?: string
}

const AD_CONFIGS = {
  'sidebar-160x600': {
    width: 160,
    height: 600,
  },
  'sidebar-160x300': {
    width: 160,
    height: 300,
  },
}

export function SidebarAd({ type, className = '', adKey }: SidebarAdProps) {
  // 如果 adKey 未配置或为空，不渲染
  if (!adKey || adKey === '0') {
    return null
  }

  const config = AD_CONFIGS[type]

  return (
    <div className={`flex justify-center ${className}`}>
      <iframe
        src={`/ads/${type}.html`}
        width={config.width}
        height={config.height}
        style={{ border: 'none', maxWidth: '100%', display: 'block' }}
        title={`Adsterra ${type} Sidebar Ad`}
        scrolling="no"
      />
    </div>
  )
}

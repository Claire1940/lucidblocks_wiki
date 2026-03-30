'use client'

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

/**
 * 横幅广告组件 (iframe方式)
 * 使用 Adsterra 横幅广告
 * 使用固定尺寸显示，避免iframe内出现滚动条
 */
export function AdBanner({ type, className = '', adKey }: AdBannerProps) {
  // 如果 adKey 未配置或为空，不渲染
  if (!adKey || adKey === '0') {
    return null
  }

  const config = AD_CONFIGS[type]

  return (
    <div className={`flex justify-center ${className}`}>
      <div style={{ maxWidth: `${config.width}px`, width: '100%' }}>
        <iframe                                                                                                 
        src={`/ads/${type}.html`}                                                                                    
        width={config.width}                                                                                  
        height={config.height}                                                                                
        style={{ border: 'none', maxWidth: '100%', display: 'block' }}                                        
        title={`Adsterra ${type} Banner`}                                                                     
        scrolling="no"                                                                                        
      />
      </div>
    </div>
  )
}

import { getIcon, hasIcon } from '@/lib/iconRegistry'
import type { LucideIcon } from 'lucide-react'

interface DynamicIconProps {
  name: string
  className?: string
  size?: number
  fallback?: LucideIcon
}

/**
 * 动态图标组件 - 根据名称渲染图标
 *
 * @example
 * <DynamicIcon name="Download" className="w-6 h-6" />
 */
export function DynamicIcon({
  name,
  className = '',
  size,
  fallback
}: DynamicIconProps) {
  const IconComponent = getIcon(name)

  // 开发环境下的额外警告
  if (process.env.NODE_ENV === 'development' && !hasIcon(name)) {
    console.warn(
      `[DynamicIcon] Icon "${name}" not found in registry. ` +
      `Add it to src/lib/iconRegistry.ts`
    )
  }

  return (
    <IconComponent
      className={className}
      size={size}
      aria-hidden="true"
    />
  )
}

import type { LucideIcon } from 'lucide-react'

interface SectionProps {
  icon?: string | LucideIcon
  title: string
  children: React.ReactNode
}

export function Section({ icon, title, children }: SectionProps) {
  // 判断 icon 是否为 Lucide 图标组件
  const IconComponent = icon && typeof icon !== 'string' ? icon : null

  return (
    <section className="py-1">
      <div className="container mx-auto max-w-6xl px-4">
        <div className="flex items-center gap-3 mb-0">
          {icon && (
            <>
              {typeof icon === 'string' ? (
                // 向后兼容：支持 emoji 字符串
                <span className="text-3xl leading-none translate-y-1">
                  {icon}
                </span>
              ) : IconComponent ? (
                // 推荐：使用 Lucide 图标组件
                <IconComponent className="w-8 h-8 text-gray-700 dark:text-gray-300 flex-shrink-0 translate-y-3" />
              ) : null}
            </>
          )}
          <h2 className="text-3xl font-bold text-foreground leading-none">{title}</h2>
        </div>
        {children}
      </div>
    </section>
  )
}

import { Info, AlertCircle, CheckCircle, Lightbulb } from 'lucide-react'

interface CalloutProps {
  type?: 'info' | 'warning' | 'success' | 'tip'
  title?: string
  children: React.ReactNode
}

export function Callout({ type = 'info', title, children }: CalloutProps) {
  const styles = {
    // 亮色主题样式
    light: {
      info: 'bg-blue-50 border-blue-200 text-blue-900',
      warning: 'bg-yellow-50 border-yellow-200 text-yellow-900',
      success: 'bg-emerald-50 border-emerald-200 text-emerald-900',
      tip: 'bg-green-50 border-green-200 text-green-900',
    },
    // 暗色主题样式 - 使用半透明效果
    dark: {
      info: 'dark:bg-blue-900/20 dark:border-blue-500/30 dark:text-blue-300',
      warning: 'dark:bg-yellow-900/20 dark:border-yellow-700/50 dark:text-yellow-200',
      success: 'dark:bg-emerald-900/20 dark:border-emerald-500/30 dark:text-emerald-300',
      tip: 'dark:bg-green-900/20 dark:border-green-500/30 dark:text-green-300',
    },
  }

  const combinedStyles = {
    info: `${styles.light.info} ${styles.dark.info}`,
    warning: `${styles.light.warning} ${styles.dark.warning}`,
    success: `${styles.light.success} ${styles.dark.success}`,
    tip: `${styles.light.tip} ${styles.dark.tip}`,
  }

  const icons = {
    info: <Info className="w-5 h-5" />,
    warning: <AlertCircle className="w-5 h-5" />,
    success: <CheckCircle className="w-5 h-5" />,
    tip: <Lightbulb className="w-5 h-5" />,
  }

  return (
    <div className={`p-6 rounded-xl border ${combinedStyles[type]} my-6`}>
      <div className="flex gap-3 items-start">
        <div className="flex-shrink-0 mt-1.5">{icons[type]}</div>
        <div className="flex-1">
          {title && <div className="font-bold mb-2">{title}</div>}
          <div>{children}</div>
        </div>
      </div>
    </div>
  )
}

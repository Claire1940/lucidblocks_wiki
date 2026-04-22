import { routing, type Locale } from '@/i18n/routing'

/**
 * 动态构建语言替代链接配置
 * @param path - 页面路径（如 '/', '/codes' 等）
 * @param locale - 当前语言
 * @param baseUrl - 网站基础URL
 * @returns 包含 canonical 和 languages 的配置对象
 */
export function buildLanguageAlternates(path: string, locale: Locale, baseUrl: string) {
  // 强制 https 协议，避免 NEXT_PUBLIC_SITE_URL 被注入 http:// 导致 hreflang Link 头泄漏
  baseUrl = baseUrl.replace(/^http:\/\//i, 'https://')
  // 规范化路径：移除尾部斜杠（除非是根路径）
  const normalizedPath = path === '/' ? '' : path.replace(/\/$/, '')

  const languages: Record<string, string> = {}

  // 从 routing.locales 动态构建所有语言的URL
  for (const loc of routing.locales) {
    const url = loc === 'en' ? `${baseUrl}${normalizedPath}` : `${baseUrl}/${loc}${normalizedPath}`
    languages[loc] = url
  }

  // 添加默认语言标识
  languages['x-default'] = `${baseUrl}${normalizedPath}`

  return {
    canonical: locale === 'en' ? `${baseUrl}${normalizedPath}` : `${baseUrl}/${locale}${normalizedPath}`,
    languages,
  }
}

/**
 * 获取所有支持的语言列表
 * @returns 语言代码数组
 */
export function getSupportedLocales(): readonly Locale[] {
  return routing.locales
}

/**
 * 检查语言代码是否有效
 * @param locale - 要检查的语言代码
 * @returns 是否为有效语言
 */
export function isValidLocale(locale: string): locale is Locale {
  return (routing.locales as readonly string[]).includes(locale)
}

/**
 * 获取默认语言
 * @returns 默认语言代码
 */
export function getDefaultLocale(): Locale {
  return routing.defaultLocale
}

/**
 * 动态生成语言显示名称
 * 自动从语言代码生成显示名称，无需硬编码
 * @returns 语言代码到显示名称的映射
 */
export function getLanguageDisplayNames(): Record<Locale, string> {
  const result: Record<Locale, string> = {} as Record<Locale, string>

  // 动态生成显示名称：直接使用语言代码的大写形式
  // 这样添加新语言时无需修改此文件
  routing.locales.forEach(locale => {
    result[locale] = locale.toUpperCase()
  })

  return result
}
/**
 * 类型安全的翻译 Hook
 *
 * 替代 useMessages() as any，提供完整的类型安全
 */

import { useMessages } from 'next-intl'
import { useMemo } from 'react'
import type { Translations } from '@/lib/translationSchema'

/**
 * 使用类型安全的翻译
 *
 * @example
 * const t = useTypedMessages()
 * const title = t.hero.title  // ✅ 类型安全
 * const cards = t.tools.cards || []  // ✅ 安全访问可选字段
 */
export function useTypedMessages(): Translations {
  const messages = useMessages()
  return messages as Translations
}

/**
 * 安全地获取数组数据
 *
 * @example
 * const cards = useSafeArray(t.tools.cards)
 * // 如果 cards 是 undefined，返回空数组
 */
export function useSafeArray<T>(arr: T[] | undefined | null): T[] {
  return useMemo(() => {
    if (!arr || !Array.isArray(arr)) {
      return []
    }
    return arr
  }, [arr])
}

/**
 * 安全地获取对象数据
 *
 * @example
 * const module = useSafeObject(t.modules.demoDownload, {
 *   title: '',
 *   subtitle: '',
 *   sections: []
 * })
 */
export function useSafeObject<T extends object>(
  obj: T | undefined | null,
  defaultValue: T
): T {
  return useMemo(() => {
    return obj || defaultValue
  }, [obj, defaultValue])
}

/**
 * 检查数据是否存在且有效
 *
 * @example
 * const hasCards = useHasData(t.tools.cards)
 * if (hasCards) {
 *   // 渲染卡片
 * }
 */
export function useHasData<T>(data: T[] | undefined | null): boolean {
  return useMemo(() => {
    return Array.isArray(data) && data.length > 0
  }, [data])
}

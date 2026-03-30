/**
 * 类型安全的卡片列表组件示例
 *
 * 展示如何使用三层架构：
 * 1. 数据层（JSON）- 字段可选
 * 2. 适配层（这个组件）- 验证和转换
 * 3. 组件层（IconCardList）- 字段必需
 */

import { useTypedMessages, useSafeArray, useHasData } from '@/hooks/useTypedMessages'
import type { IconCard } from '@/lib/translationSchema'

// ============================================
// 组件层：要求数据必须存在
// ============================================

interface IconCardListProps {
  cards: IconCard[]  // 必需！
  onCardClick?: (index: number) => void
}

function IconCardList({ cards, onCardClick }: IconCardListProps) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
      {cards.map((card, index) => (
        <button
          key={index}
          onClick={() => onCardClick?.(index)}
          className="p-6 rounded-xl border border-border bg-card hover:border-primary transition-all"
        >
          <div className="w-12 h-12 rounded-lg mb-4 bg-primary/10 flex items-center justify-center">
            {/* 图标渲染 */}
          </div>
          <h3 className="font-semibold mb-2">{card.title}</h3>
          <p className="text-sm text-muted-foreground">{card.description}</p>
        </button>
      ))}
    </div>
  )
}

// ============================================
// 适配层：验证和转换数据
// ============================================

export function ToolsSection() {
  // 使用类型安全的 hook
  const t = useTypedMessages()

  // 安全地获取数组（如果不存在返回空数组）
  const cards = useSafeArray(t.tools.cards)

  // 检查是否有数据
  const hasCards = useHasData(t.tools.cards)

  // 如果没有数据，显示空状态
  if (!hasCards) {
    return (
      <section className="px-4 py-20">
        <div className="container mx-auto text-center">
          <p className="text-muted-foreground">No tools available</p>
        </div>
      </section>
    )
  }

  // 有数据，传递给组件（此时保证 cards 不为空）
  return (
    <section className="px-4 py-20">
      <div className="container mx-auto">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold mb-4">
            {t.tools.title}{' '}
            <span className="text-primary">{t.tools.titleHighlight}</span>
          </h2>
          <p className="text-muted-foreground text-lg">{t.tools.subtitle}</p>
        </div>

        {/* 传递给组件时，cards 保证是有效数组 */}
        <IconCardList
          cards={cards}
          onCardClick={(index) => {
            console.log('Clicked card:', index)
          }}
        />
      </div>
    </section>
  )
}

// ============================================
// 使用示例对比
// ============================================

/*
❌ 旧的不安全方式：

const t = useMessages() as any

return (
  <div>
    {t.tools.cards.map((card: any) => (  // 💥 如果 cards 是 undefined 会崩溃
      <div>{card.title}</div>
    ))}
  </div>
)

✅ 新的类型安全方式：

const t = useTypedMessages()  // 类型安全
const cards = useSafeArray(t.tools.cards)  // 安全获取，不会崩溃
const hasCards = useHasData(t.tools.cards)  // 检查是否有数据

if (!hasCards) {
  return <EmptyState />  // 优雅降级
}

return <IconCardList cards={cards} />  // 传递时保证数据有效
*/

'use client'

import { useState, useEffect } from 'react'

interface ChecklistProps {
  id: string
  title: string
  items: string[]
}

// 解析 Markdown 粗体标记 (**text** -> <strong>text</strong>)
function parseMarkdown(text: string) {
  const parts = text.split(/(\*\*.*?\*\*)/)

  return parts.map((part, index) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      const content = part.slice(2, -2)
      return <strong key={index} className="font-bold text-foreground">{content}</strong>
    }
    return part
  })
}

export function Checklist({ id, title, items }: ChecklistProps) {
  const [checkedItems, setCheckedItems] = useState<Set<number>>(new Set())

  // 从 localStorage 加载勾选状态
  useEffect(() => {
    const saved = localStorage.getItem(`checklist-${id}`)
    if (saved) {
      try {
        const parsed = JSON.parse(saved)
        setCheckedItems(new Set(parsed))
      } catch (e) {
        console.error('Failed to parse checklist data:', e)
      }
    }
  }, [id])

  // 保存勾选状态到 localStorage
  const toggleItem = (index: number) => {
    setCheckedItems(prev => {
      const newSet = new Set(prev)
      if (newSet.has(index)) {
        newSet.delete(index)
      } else {
        newSet.add(index)
      }
      localStorage.setItem(`checklist-${id}`, JSON.stringify([...newSet]))
      return newSet
    })
  }

  return (
    <div className="mb-4">
      <h3 className="text-xl font-bold text-foreground mb-2">{title}</h3>
      <ul className="space-y-1.5">
        {items.map((item, index) => (
          <li key={index} className="flex items-start gap-3">
            <button
              onClick={() => toggleItem(index)}
              className="flex-shrink-0 w-5 h-5 mt-0.5 rounded border-2 border-muted-foreground hover:border-blue-400 transition-colors flex items-center justify-center cursor-pointer"
              aria-label={checkedItems.has(index) ? 'Uncheck item' : 'Check item'}
            >
              {checkedItems.has(index) && (
                <svg
                  className="w-4 h-4 text-blue-400"
                  fill="none"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path d="M5 13l4 4L19 7" />
                </svg>
              )}
            </button>
            <span className={`text-muted-foreground ${checkedItems.has(index) ? 'line-through opacity-60' : ''}`}>
              {parseMarkdown(item)}
            </span>
          </li>
        ))}
      </ul>
    </div>
  )
}

import React from 'react'

interface FAQItemProps {
  question: string
  answer: string
}

export function FAQItem({ question, answer }: FAQItemProps) {
  return (
    <div className="mb-6">
      <p className="font-bold text-foreground text-lg mb-2">
        Q: {question}
      </p>
      <p className="text-muted-foreground leading-relaxed pl-4">
        {answer}
      </p>
    </div>
  )
}

interface FAQProps {
  items: Array<{ question: string; answer: string }>
}

export function FAQ({ items }: FAQProps) {
  return (
    <div className="space-y-4">
      {items.map((item, index) => (
        <FAQItem key={index} question={item.question} answer={item.answer} />
      ))}
    </div>
  )
}

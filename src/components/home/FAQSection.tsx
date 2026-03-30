'use client'

import { useState } from 'react'
import { ChevronDown } from 'lucide-react'

interface FAQItem {
  question: string
  answer: string
}

interface FAQSectionProps {
  title: string
  titleHighlight: string
  subtitle: string
  questions: FAQItem[]
}

export default function FAQSection({ title, titleHighlight, subtitle, questions }: FAQSectionProps) {
  const [expandedFaq, setExpandedFaq] = useState<number | null>(null)

  const toggleFaq = (index: number) => {
    setExpandedFaq(expandedFaq === index ? null : index)
  }

  return (
    <section className="px-4 py-20">
      <div className="container mx-auto max-w-4xl">
        <div className="text-center mb-12">
          <h2 className="scroll-reveal text-4xl md:text-5xl font-bold mb-4">
            {title} <span className="text-[hsl(var(--nav-theme-light))]">{titleHighlight}</span>
          </h2>
          <p className="scroll-reveal text-muted-foreground text-lg">
            {subtitle}
          </p>
        </div>

        <div className="space-y-4">
          {questions.map((item, index) => (
            <div
              key={index}
              className="scroll-reveal p-6 bg-white/5 border border-border rounded-xl hover:border-[hsl(var(--nav-theme)/0.5)] transition"
            >
              <button
                onClick={() => toggleFaq(index)}
                className="flex items-center justify-between w-full text-left"
                aria-expanded={expandedFaq === index}
              >
                <h3 className="font-semibold">{item.question}</h3>
                <ChevronDown
                  className={`w-5 h-5 text-muted-foreground group-hover:text-[hsl(var(--nav-theme-light))] transition-transform duration-300 ${
                    expandedFaq === index ? 'rotate-180' : ''
                  }`}
                />
              </button>

              {/* 答案内容 - 带动画 */}
              <div
                className={`overflow-hidden transition-all duration-300 ease-in-out ${
                  expandedFaq === index ? 'max-h-96 mt-4 opacity-100' : 'max-h-0 opacity-0'
                }`}
              >
                <p className="text-muted-foreground text-sm leading-relaxed">
                  {item.answer}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
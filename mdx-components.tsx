import type { MDXComponents } from 'mdx/types'
import { Section } from '@/components/mdx/Section'
import { CardGrid, Card } from '@/components/mdx/CardGrid'
import { Callout } from '@/components/mdx/Callout'
import { Steps, Step } from '@/components/mdx/Steps'
import { CTAButtons } from '@/components/mdx/CTAButtons'
import { Checklist } from '@/components/mdx/Checklist'
import { YouTubeEmbed } from '@/components/mdx/YouTubeEmbed'
import { FAQ, FAQItem } from '@/components/mdx/FAQ'

export function useMDXComponents(components: MDXComponents): MDXComponents {
  return {
    // 自定义组件
    Section,
    CardGrid,
    Card,
    Callout,
    Steps,
    Step,
    CTAButtons,
    Checklist,
    YouTubeEmbed,
    FAQ,
    FAQItem,

    // 覆盖默认 HTML 元素
    h1: (props) => <h1 className="text-4xl font-bold text-white mb-3" {...props} />,
    h2: (props) => <h2 className="text-3xl font-bold text-white mb-2 mt-4" {...props} />,
    h3: (props) => <h3 className="text-2xl font-bold text-white mb-2 mt-4" {...props} />,
    p: (props) => <p className="text-slate-300 leading-tight mb-3" {...props} />,
    ul: (props) => <ul className="list-disc pl-6 space-y-1 text-slate-300 mb-3" {...props} />,
    ol: (props) => <ol className="list-decimal pl-6 space-y-1 text-slate-300 mb-3" {...props} />,
    li: (props) => <li className="text-slate-300" {...props} />,
    strong: (props) => <strong className="font-bold text-white" {...props} />,
    em: (props) => <em className="italic text-slate-200" {...props} />,
    code: (props) => (
      <code className="px-1.5 py-0.5 rounded bg-slate-800 text-blue-400 text-sm font-mono" {...props} />
    ),
    pre: (props) => (
      <pre className="bg-slate-900 border border-slate-800 rounded-lg p-4 overflow-x-auto mb-4" {...props} />
    ),
    blockquote: (props) => (
      <blockquote className="border-l-4 border-blue-500 pl-4 py-2 my-4 text-slate-300 italic" {...props} />
    ),
    table: (props) => (
      <div className="overflow-x-auto my-6">
        <table className="min-w-full border-collapse border border-slate-700" {...props} />
      </div>
    ),
    thead: (props) => <thead className="bg-slate-800" {...props} />,
    tbody: (props) => <tbody className="bg-slate-900/50" {...props} />,
    tr: (props) => <tr className="border-b border-slate-700" {...props} />,
    th: (props) => (
      <th className="px-4 py-3 text-center text-sm font-semibold text-white border border-slate-700 bg-slate-800" {...props} />
    ),
    td: (props) => (
      <td className="px-4 py-3 text-center text-sm text-slate-300 border border-slate-700" {...props} />
    ),
    a: (props) => (
      <a className="text-blue-400 hover:text-blue-300 underline underline-offset-2 transition-colors" {...props} />
    ),

    ...components,
  }
}

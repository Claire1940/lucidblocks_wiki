'use client'

import Link from 'next/link'
import type { ContentItem } from '@/lib/content'

interface ContentItemWithType extends ContentItem {
  contentType: string
}

interface LatestGuidesAccordionProps {
  articles: ContentItemWithType[]
  locale: string
  max?: number
  className?: string
}

function AccordionColumn({ articles, locale }: { articles: ContentItemWithType[]; locale: string }) {
  return (
    <div
      className="bg-white/5 border border-border rounded-xl overflow-hidden"
      role="region"
      aria-label="Latest articles"
    >
      {articles.map((article, index) => {
        const url = `/${locale}/${article.contentType}/${article.slug}`
        const detailsId = `article-${article.contentType}-${article.slug}`

        return (
          <details
            key={`${article.contentType}-${article.slug}`}
            className={`group ${index !== articles.length - 1 ? 'border-b border-border' : ''}`}
          >
            <summary
              className="cursor-pointer py-4 px-6 text-sm font-medium
                         hover:bg-white/5 transition-colors
                         flex items-center justify-between
                         list-none [&::-webkit-details-marker]:hidden"
              id={`${detailsId}-header`}
              aria-controls={`${detailsId}-content`}
            >
              <span className="flex-1 group-hover:text-[hsl(var(--nav-theme-light))] transition-colors">
                {article.frontmatter.title}
              </span>

              {/* 展开/收起图标 */}
              <svg
                className="w-5 h-5 text-muted-foreground transition-transform group-open:rotate-180"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </summary>

            <div
              className="px-6 pb-4"
              id={`${detailsId}-content`}
              role="region"
              aria-labelledby={`${detailsId}-header`}
            >
              {/* 摘要 */}
              {article.frontmatter.description && (
                <p className="pl-4 text-xs text-muted-foreground py-1 line-clamp-3 mb-2">
                  {article.frontmatter.description}
                </p>
              )}

              {/* 元信息 */}
              <div className="pl-4 flex items-center gap-4 text-xs text-muted-foreground mb-2">
                {article.frontmatter.date && (
                  <span>
                    {new Date(article.frontmatter.date).toLocaleDateString(locale, {
                      year: 'numeric',
                      month: 'short',
                      day: 'numeric'
                    })}
                  </span>
                )}
                <span className="text-[hsl(var(--nav-theme-light))] uppercase tracking-wider">
                  {article.contentType}
                </span>
              </div>

              {/* Read more 链接 */}
              <Link
                href={url}
                className="pl-4 text-xs text-[hsl(var(--nav-theme-light))] hover:underline inline-flex items-center gap-1"
              >
                Read more →
              </Link>
            </div>
          </details>
        )
      })}
    </div>
  )
}

export function LatestGuidesAccordion({
  articles,
  locale,
  max = 30,
  className = ''
}: LatestGuidesAccordionProps) {
  const displayArticles = articles.slice(0, max)

  if (displayArticles.length === 0) {
    return null
  }

  // 分成两列：前半放左列，后半放右列
  const midpoint = Math.ceil(displayArticles.length / 2)
  const leftColumn = displayArticles.slice(0, midpoint)
  const rightColumn = displayArticles.slice(midpoint)

  return (
    <section className={`px-4 py-20 ${className}`}>
      <div className="container mx-auto max-w-6xl">
        {/* 标题 */}
        <div className="text-center mb-12 scroll-reveal">
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            Latest <span className="text-[hsl(var(--nav-theme-light))]">Updates</span>
          </h2>
          <p className="text-muted-foreground text-lg">
            Discover the newest guides, tips, and content
          </p>
        </div>

        {/* 双列手风琴 */}
        <div className="scroll-reveal grid grid-cols-1 md:grid-cols-2 gap-6">
          <AccordionColumn articles={leftColumn} locale={locale} />
          {rightColumn.length > 0 && (
            <AccordionColumn articles={rightColumn} locale={locale} />
          )}
        </div>

      </div>
    </section>
  )
}

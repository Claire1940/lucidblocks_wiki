'use client'

import Link from 'next/link'
import type { ContentItem } from '@/lib/content'

interface ContentItemWithType extends ContentItem {
  contentType: string
}

interface LatestGuidesProps {
  articles: ContentItemWithType[]
  locale: string
  className?: string
}

export function LatestGuides({ articles, locale, className = '' }: LatestGuidesProps) {
  // 如果没有文章，不渲染
  if (articles.length === 0) {
    return null
  }

  return (
    <section className={`px-4 py-20 ${className}`}>
      <div className="container mx-auto">
        <div className="text-center mb-12 scroll-reveal">
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            Latest <span className="text-[hsl(var(--nav-theme-light))]">Updates</span>
          </h2>
          <p className="text-muted-foreground text-lg">
            Discover the newest guides, tips, and content
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 scroll-reveal">
          {articles.map((article) => {
            const url = `/${locale}/${article.contentType}/${article.slug}`

            return (
              <Link
                key={`${article.contentType}-${article.slug}`}
                href={url}
                className="group bg-white/5 border border-border rounded-xl p-6 hover:border-[hsl(var(--nav-theme)/0.5)] transition-all duration-300 hover:shadow-lg hover:shadow-[hsl(var(--nav-theme)/0.1)]"
              >
                <div className="flex flex-col h-full">
                  <h3 className="text-xl font-semibold mb-2 group-hover:text-[hsl(var(--nav-theme-light))] transition-colors">
                    {article.frontmatter.title}
                  </h3>

                  {article.frontmatter.description && (
                    <p className="text-muted-foreground text-sm mb-4 line-clamp-2 flex-grow">
                      {article.frontmatter.description}
                    </p>
                  )}

                  <div className="flex items-center justify-between mt-auto pt-4 border-t border-border/50">
                    {article.frontmatter.date && (
                      <span className="text-xs text-muted-foreground">
                        {new Date(article.frontmatter.date).toLocaleDateString(locale, {
                          year: 'numeric',
                          month: 'short',
                          day: 'numeric'
                        })}
                      </span>
                    )}

                    <span className="text-xs text-[hsl(var(--nav-theme-light))] uppercase tracking-wider">
                      {article.contentType}
                    </span>
                  </div>
                </div>
              </Link>
            )
          })}
        </div>

      </div>
    </section>
  )
}

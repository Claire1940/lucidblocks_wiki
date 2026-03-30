import { Link } from '@/i18n/navigation'
import { ContentItem } from '@/lib/content'
import { useTranslations } from 'next-intl'
import { ArrowRight } from 'lucide-react'
import { extractPrimaryKeyword } from '@/lib/utils'

interface RelatedArticlesProps {
	articles: ContentItem[]
	contentType: string
}

export function RelatedArticles({ articles, contentType }: RelatedArticlesProps) {
	const t = useTranslations()

	if (articles.length === 0) {
		return null
	}

	return (
		<div className="mt-16 pt-8 border-t border-border">
			<h2 className="text-2xl font-bold text-foreground mb-6">{t('common.relatedArticles')}</h2>
			<div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
				{articles.slice(0, 3).map((article) => (
					<Link
						key={article.slug}
						href={`/${contentType}/${article.slug}`}
						className="group block p-4 rounded-xl bg-card/50 border border-border hover:border-blue-500/50 hover:bg-card transition-all"
					>
						<h3 className="text-lg font-semibold text-foreground group-hover:text-blue-400 transition-colors mb-2">
							{extractPrimaryKeyword(article.frontmatter.title)}
						</h3>
						<p className="text-sm text-muted-foreground line-clamp-2 mb-3">
							{article.frontmatter.description}
						</p>
						<span className="inline-flex items-center gap-1 text-sm text-blue-400 group-hover:gap-2 transition-all">
							{t('common.readMore')}
							<ArrowRight className="w-4 h-4" />
						</span>
					</Link>
				))}
			</div>
		</div>
	)
}

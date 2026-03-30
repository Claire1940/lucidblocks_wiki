import { MetadataRoute } from 'next'
import { getAllContent, CONTENT_TYPES, type ContentType } from '@/lib/content'
import { routing, type Locale } from '@/i18n/routing'

const BASE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://www.lucidblocks.wiki'

// 静态页面配置
const staticPagesConfig: Record<string, { priority: number; changeFrequency: 'monthly' | 'yearly' }> = {
	'about': { priority: 0.6, changeFrequency: 'monthly' },
	'privacy-policy': { priority: 0.3, changeFrequency: 'yearly' },
	'terms-of-service': { priority: 0.3, changeFrequency: 'yearly' },
	'copyright': { priority: 0.3, changeFrequency: 'yearly' },
}

// 内容类型优先级配置
const contentTypePriority: Record<string, number> = {
	'guides': 0.9,
	'crafting': 0.9,
	'biomes': 0.8,
	'creatures': 0.8,
	'items': 0.8,
	'achievements': 0.7,
	'lore': 0.7,
	'support': 0.6,
}

// 内容更新频率配置
const contentTypeChangeFrequency: Record<string, 'daily' | 'weekly' | 'monthly'> = {
	'guides': 'weekly',
	'crafting': 'weekly',
	'biomes': 'weekly',
	'creatures': 'weekly',
	'items': 'weekly',
	'achievements': 'monthly',
	'lore': 'monthly',
	'support': 'monthly',
}

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
	const sitemap: MetadataRoute.Sitemap = []

	// 1. 首页（所有语言版本）
	for (const locale of routing.locales) {
		sitemap.push({
			url: locale === 'en' ? BASE_URL : `${BASE_URL}/${locale}`,
			lastModified: new Date(),
			changeFrequency: 'daily',
			priority: 1.0,
		})
	}

	// 2. 静态页面（所有语言版本）
	const staticPages = ['about', 'privacy-policy', 'terms-of-service', 'copyright']
	for (const locale of routing.locales) {
		for (const page of staticPages) {
			const config = staticPagesConfig[page] || { priority: 0.5, changeFrequency: 'monthly' as const }
			sitemap.push({
				url: locale === 'en' ? `${BASE_URL}/${page}` : `${BASE_URL}/${locale}/${page}`,
				lastModified: new Date(),
				changeFrequency: config.changeFrequency,
				priority: config.priority,
			})
		}
	}

	// 3. 所有 MDX 文章（所有语言版本和内容类型）
	for (const locale of routing.locales) {
		for (const contentType of CONTENT_TYPES) {
			try {
				// 获取该语言和内容类型的所有文章
				const articles = await getAllContent(contentType as ContentType, locale as Locale)

				for (const article of articles) {
					// 构建完整的文章 URL
					const articleUrl =
						locale === 'en'
							? `${BASE_URL}/${contentType}/${article.slug}`
							: `${BASE_URL}/${locale}/${contentType}/${article.slug}`

					// 获取该内容类型的优先级和更新频率
					const priority = contentTypePriority[contentType] || 0.7
					const changeFrequency = contentTypeChangeFrequency[contentType] || 'weekly'

					sitemap.push({
						url: articleUrl,
						lastModified: article.frontmatter.date
							? new Date(article.frontmatter.date)
							: new Date(),
						changeFrequency: changeFrequency,
						priority: priority,
					})
				}
			} catch (error) {
				// 忽略无法加载的内容类型
				console.warn(`Failed to load content for ${locale}/${contentType}:`, error)
			}
		}
	}

	return sitemap
}

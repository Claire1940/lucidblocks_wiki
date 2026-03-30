import type { ContentFrontmatter, ContentType } from '@/lib/content'

interface ListStructuredDataProps {
	contentType: ContentType
	locale: string
	items: Array<{ slug: string; frontmatter: ContentFrontmatter }>
}

export function ListStructuredData({ contentType, locale, items }: ListStructuredDataProps) {
	const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || 'https://www.lucidblocks.wiki'
	const listUrl =
		locale === 'en' ? `${siteUrl}/${contentType}` : `${siteUrl}/${locale}/${contentType}`

	const structuredData = {
		'@context': 'https://schema.org',
		'@type': 'ItemList',
		itemListElement: items.map((item, index) => ({
			'@type': 'ListItem',
			position: index + 1,
			url:
				locale === 'en'
					? `${siteUrl}/${contentType}/${item.slug}`
					: `${siteUrl}/${locale}/${contentType}/${item.slug}`,
			name: item.frontmatter.title,
		})),
	}

	return (
		<script
			type="application/ld+json"
			dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }}
		/>
	)
}

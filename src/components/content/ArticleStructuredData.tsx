import type { ContentFrontmatter, ContentType } from '@/lib/content'

interface ArticleStructuredDataProps {
	frontmatter: ContentFrontmatter
	contentType: ContentType
	locale: string
	slug: string
}

export function ArticleStructuredData({
	frontmatter,
	contentType,
	locale,
	slug,
}: ArticleStructuredDataProps) {
	const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || 'https://www.lucidblocks.wiki'
	const articleUrl =
		locale === 'en'
			? `${siteUrl}/${contentType}/${slug}`
			: `${siteUrl}/${locale}/${contentType}/${slug}`

	const breadcrumbData = {
		'@context': 'https://schema.org',
		'@type': 'BreadcrumbList',
		itemListElement: [
			{
				'@type': 'ListItem',
				position: 1,
				name: 'Home',
				item: siteUrl,
			},
			{
				'@type': 'ListItem',
				position: 2,
				name: contentType.charAt(0).toUpperCase() + contentType.slice(1),
				item: `${siteUrl}/${contentType}`,
			},
			{
				'@type': 'ListItem',
				position: 3,
				name: frontmatter.title,
				item: articleUrl,
			},
		],
	}

	const structuredData = {
		'@context': 'https://schema.org',
		'@type': 'Article',
		headline: frontmatter.title,
		description: frontmatter.description,
		image: frontmatter.image || `${siteUrl}/default-article-image.jpg`,
		datePublished: frontmatter.date,
		dateModified: ('lastModified' in frontmatter && frontmatter.lastModified) || frontmatter.date,
		author: {
			'@type': 'Organization',
			name: 'Lucid Blocks Wiki Team',
		},
		publisher: {
			'@type': 'Organization',
			name: 'Lucid Blocks Wiki',
			logo: {
				'@type': 'ImageObject',
				url: `${siteUrl}/images/hero.webp`,
			},
		},
		mainEntityOfPage: {
			'@type': 'WebPage',
			'@id': articleUrl,
		},
	}

	return (
		<>
			<script
				type="application/ld+json"
				dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }}
			/>
			<script
				type="application/ld+json"
				dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbData) }}
			/>
		</>
	)
}

import { NAVIGATION_CONFIG } from '@/config/navigation'
import { getAllContent, type Language } from '@/lib/content'
import type { NavPreviewData } from '@/types/nav-preview'

export async function getNavPreviewData(locale: Language): Promise<NavPreviewData> {
	const data: NavPreviewData = {}

	for (const item of NAVIGATION_CONFIG) {
		if (!item.isContentType) continue
		const type = item.path.slice(1)
		const items = await getAllContent(type, locale)
		data[type] = items.map((i) => ({
			slug: i.slug,
			title: i.frontmatter.title,
		}))
	}

	return data
}

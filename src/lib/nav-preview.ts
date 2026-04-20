import { NAVIGATION_CONFIG } from '@/config/navigation'
import { getAllContent, type Language } from '@/lib/content'
import type { NavPreviewData } from '@/types/nav-preview'

export async function getNavPreviewData(locale: Language): Promise<NavPreviewData> {
	const data: NavPreviewData = {}

	for (const item of NAVIGATION_CONFIG) {
		if (!item.isContentType) continue
		const type = item.path.slice(1)
		const items = await getAllContent(type, locale)
		// 导航栏内按「最早更新」升序（优先 lastModified，回退 date），
		// 与首页/列表页「最近更新」降序相反
		const sorted = items.slice().sort((a, b) => {
			const getTime = (i: (typeof items)[number]) => {
				const fm = i.frontmatter
				if (!fm) return 0
				if (fm.lastModified) return new Date(fm.lastModified).getTime()
				if (fm.date) return new Date(fm.date).getTime()
				return 0
			}
			return getTime(a) - getTime(b)
		})
		data[type] = sorted.map((i) => ({
			slug: i.slug,
			title: i.frontmatter.title,
		}))
	}

	return data
}

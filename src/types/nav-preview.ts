export interface NavPreviewArticle {
	slug: string
	title: string
}

export type NavPreviewData = Record<string, NavPreviewArticle[]>

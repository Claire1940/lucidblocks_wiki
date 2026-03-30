import { Link } from '@/i18n/navigation'
import Image from 'next/image'
import { ContentFrontmatter, ContentItem, Language } from '@/lib/content'
import { Calendar, User, ArrowLeft } from 'lucide-react'
import { getTranslations } from 'next-intl/server'
import { RelatedArticles } from './RelatedArticles'
import { extractPlaceholderMetadata, getTailwindRgbString } from '@/lib/imageUtils'
import { extractPrimaryKeyword } from '@/lib/utils'
import { SidebarAd } from '@/components/ads/SidebarAd'
import { AdBanner } from '@/components/ads'

interface DetailPageProps {
	frontmatter: ContentFrontmatter
	content: React.ReactNode // 接受 ReactNode
	contentType: string
	language: Language
	currentSlug: string
	relatedArticles: ContentItem[]
}

export async function DetailPage({ frontmatter, content, contentType, language, currentSlug, relatedArticles }: DetailPageProps) {
	// 服务端加载翻译
	const t = await getTranslations()

	// 内容类型翻译映射
	const contentTypeLabels: Record<string, string> = {
		guides: t('nav.guides'),
		crafting: t('nav.crafting'),
		items: t('nav.items'),
		biomes: t('nav.biomes'),
		building: t('nav.building'),
		support: t('nav.support'),
	}

	// 提取图片元数据
	const imageMetadata = frontmatter.image ? extractPlaceholderMetadata(frontmatter.image) : null

	// 生成动态颜色（优先使用手动配置，然后是图片提取，最后是默认值）
	const bgColor = frontmatter.themeColor || imageMetadata?.backgroundColor || '3b82f6'
	const bgColorRgb = getTailwindRgbString(bgColor)

	// 背景文字（优先使用手动配置，然后是图片提取，最后是标题）
	const backgroundText = frontmatter.backgroundText || imageMetadata?.text || frontmatter.title

	return (
		<div className="bg-background min-h-screen">
			{/* Hero Section */}
			<section className="relative py-12 px-4">
				{/* 动态渐变背景 */}
				<div
					className="absolute inset-0 bg-gradient-to-b to-transparent"
					style={{
						backgroundImage: `linear-gradient(to bottom, rgb(${bgColorRgb} / 0.1), transparent)`,
					}}
				/>

				{frontmatter.image && (
					<div className="absolute inset-0 opacity-20">
						<Image
							src={frontmatter.image}
							alt={`${frontmatter.title} - ${contentTypeLabels[contentType] || contentType}`}
							fill
							className="object-cover"
							unoptimized
						/>
						<div className="absolute inset-0 bg-gradient-to-b from-background/50 to-background" />
					</div>
				)}

				<div className="container mx-auto max-w-4xl relative z-10 text-center">
					{/* Breadcrumb */}
					<nav aria-label="breadcrumb" className="flex items-center justify-center gap-2 text-sm text-muted-foreground mb-4">
						<Link href="/" className="hover:text-foreground transition">
							{t('common.home')}
						</Link>
						<span>/</span>
						<Link href={`/${contentType}`} className="hover:text-foreground transition">
							{contentTypeLabels[contentType] || contentType}
						</Link>
					</nav>

					<h1 className="text-4xl md:text-5xl font-bold text-foreground mb-4">{extractPrimaryKeyword(frontmatter.title)}</h1>

					<p className="text-xl text-muted-foreground mb-6">{frontmatter.description}</p>

					<div className="flex items-center justify-center gap-4 text-sm text-muted-foreground">
						{frontmatter.date && (
							<div className="flex items-center gap-1">
								<Calendar className="w-4 h-4" />
								<span>{frontmatter.date}</span>
							</div>
						)}
						{frontmatter.author && (
							<div className="flex items-center gap-1">
								<User className="w-4 h-4" />
								<span>{frontmatter.author}</span>
							</div>
						)}
					</div>
				</div>
			</section>

			{/* 固定广告：标题下方 - 320×50 移动端横幅 */}
			<div className="sticky top-20 z-20 border-b border-border py-2">
				<AdBanner type="banner-320x50" adKey={process.env.NEXT_PUBLIC_AD_MOBILE_320X50} />
			</div>

			{/* 左侧广告容器 - Fixed 定位 */}
			<aside
				className="hidden xl:block fixed top-20 w-40 z-10"
				style={{
					left: 'calc((100vw - 1280px) / 2 - 180px)',
				}}
			>
				{/* 左侧广告：160×600 竖幅 */}
				<SidebarAd type="sidebar-160x600" adKey={process.env.NEXT_PUBLIC_AD_SIDEBAR_160X600} />
			</aside>

			{/* 中间正文容器 - 保持原有宽度 */}
			<div className="container mx-auto px-4 py-6 max-w-7xl">
				{/* Article Content - MDX 渲染 */}
				<article className="prose prose-lg max-w-none">{content}</article>

				{/* Related Articles */}
				{relatedArticles.length > 0 && (
					<RelatedArticles articles={relatedArticles} contentType={contentType} />
				)}

				{/* Footer Navigation */}
				<div className="border-t border-border pt-12 mt-12">
					<Link
						href={`/${contentType}`}
						className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-blue-500 hover:bg-blue-600 text-white font-semibold transition-colors"
					>
						<ArrowLeft className="w-4 h-4" />
						{t('common.more')} {contentTypeLabels[contentType] || contentType}
					</Link>
				</div>

				{/* 文章底部广告区域 */}
				<div className="border-t border-border pt-12 mt-12 space-y-8">
					<div className="text-center text-sm text-muted-foreground mb-4">
						Advertisement
					</div>

					{/* 广告 1: 728×90 横幅 */}
					<AdBanner type="banner-728x90" adKey={process.env.NEXT_PUBLIC_AD_BANNER_728X90} />

					{/* 广告 2: 300×250 方形 */}
					<AdBanner type="banner-300x250" adKey={process.env.NEXT_PUBLIC_AD_BANNER_300X250} />

					{/* 广告 3: 468×60 横幅 */}
					<AdBanner type="banner-468x60" adKey={process.env.NEXT_PUBLIC_AD_BANNER_468X60} />
				</div>
			</div>

			{/* 右侧广告容器 - Fixed 定位 */}
			<aside
				className="hidden xl:block fixed top-20 w-40 z-10"
				style={{
					right: 'calc((100vw - 1280px) / 2 - 180px)',
				}}
			>
				{/* 右侧广告：160×300 方形 */}
				<SidebarAd type="sidebar-160x300" adKey={process.env.NEXT_PUBLIC_AD_SIDEBAR_160X300} />
			</aside>
		</div>
	)
}

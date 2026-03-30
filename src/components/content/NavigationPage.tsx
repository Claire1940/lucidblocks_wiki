import { Link } from '@/i18n/navigation'
import Image from 'next/image'
import { ContentItem, Language } from '@/lib/content'
import { Calendar, User, Sparkles, MapPin, Star, BookOpen } from 'lucide-react'
import { getTranslations } from 'next-intl/server'
import { extractPrimaryKeyword } from '@/lib/utils'
import { NativeBannerAd, AdBanner } from '@/components/ads'
import { Fragment } from 'react'

interface NavigationPageProps {
  title: string
  description: string
  items: ContentItem[]
  contentType: string
  language: Language
}

// 辅助函数：基于种子的确定性随机选择
// 使用简单的哈希函数生成伪随机数，确保服务器端和客户端结果一致
function seededRandom(seed: string): number {
  let hash = 0
  for (let i = 0; i < seed.length; i++) {
    const char = seed.charCodeAt(i)
    hash = ((hash << 5) - hash) + char
    hash = hash & hash // Convert to 32bit integer
  }
  return Math.abs(hash) / 2147483647
}

// 辅助函数：使用确定性算法选择 n 个元素
function getRandomItems<T>(array: T[], count: number, seed: string): T[] {
  const indices = array.map((_, i) => i)

  // 使用种子生成确定性的排序
  indices.sort((a, b) => {
    const hashA = seededRandom(`${seed}-${a}`)
    const hashB = seededRandom(`${seed}-${b}`)
    return hashA - hashB
  })

  return indices.slice(0, count).map(i => array[i])
}

export async function NavigationPage({
  title,
  description,
  items,
  contentType,
  language,
}: NavigationPageProps) {
  // 获取翻译
  const t = await getTranslations(`pages.${contentType}`)

  // 随机选择 2 个作为 Featured & Essential
  // 使用 contentType 作为种子，确保服务器端和客户端结果一致
  const featuredItems = getRandomItems(items, 2, contentType)
  // 剩余的文章
  const allItems = items.filter(item => !featuredItems.includes(item))

  return (
    <div className="bg-background min-h-screen">
      {/* Hero Section - 居中布局 */}
      <section className="relative py-12 px-4">
        <div className="absolute inset-0 bg-gradient-to-b from-[hsl(var(--nav-theme)/0.1)] to-transparent" />
        <div className="container mx-auto max-w-6xl relative z-10 text-center">
          {/* 类别标签 */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[hsl(var(--nav-theme)/0.1)] border border-[hsl(var(--nav-theme)/0.2)] text-[hsl(var(--nav-theme-light))] text-sm font-medium mb-3 uppercase tracking-wider">
            {t('categoryLabel')}
          </div>

          <h1 className="text-3xl md:text-4xl font-bold text-foreground mb-3">
            {title}
          </h1>
          <p className="text-base text-muted-foreground max-w-2xl mx-auto">
            {description}
          </p>
        </div>
      </section>

      {/* 广告位 1: Hero Section 下方 - 728×90 横幅 */}
      <AdBanner type="banner-728x90" />

      {/* What is / Why Section */}
      <section className="container mx-auto max-w-6xl px-4 py-8">
        <div className="grid md:grid-cols-10 gap-6">
          {/* What is Card - 4/10 */}
          <div className="md:col-span-4 relative overflow-hidden rounded-xl bg-card border border-border p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-lg bg-[hsl(var(--nav-theme)/0.1)] flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-[hsl(var(--nav-theme-light))]" />
              </div>
              <h2 className="text-xl font-bold text-foreground">{t('whatIs')}</h2>
            </div>
            <p className="text-muted-foreground leading-relaxed text-sm">
              {t('whatIsDescription')}
            </p>
          </div>

          {/* Why Card - 6/10 */}
          <div className="md:col-span-6 relative overflow-hidden rounded-xl bg-card border border-border p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-lg bg-green-500/10 flex items-center justify-center">
                <MapPin className="w-5 h-5 text-green-400" />
              </div>
              <h2 className="text-xl font-bold text-foreground">{t('why')}</h2>
            </div>
            <div className="space-y-4">
              <div className="flex gap-3">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-green-500/20 flex items-center justify-center text-green-400 font-bold text-sm">1</div>
                <div>
                  <h3 className="text-foreground font-semibold mb-1 text-base">{t('whySteps.step1Title')}</h3>
                  <p className="text-muted-foreground text-sm leading-relaxed">{t('whySteps.step1Description')}</p>
                </div>
              </div>
              <div className="flex gap-3">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-green-500/20 flex items-center justify-center text-green-400 font-bold text-sm">2</div>
                <div>
                  <h3 className="text-foreground font-semibold mb-1 text-base">{t('whySteps.step2Title')}</h3>
                  <p className="text-muted-foreground text-sm leading-relaxed">{t('whySteps.step2Description')}</p>
                </div>
              </div>
              <div className="flex gap-3">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-green-500/20 flex items-center justify-center text-green-400 font-bold text-sm">3</div>
                <div>
                  <h3 className="text-foreground font-semibold mb-1 text-base">{t('whySteps.step3Title')}</h3>
                  <p className="text-muted-foreground text-sm leading-relaxed">{t('whySteps.step3Description')}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Featured & Essential - 随机 2 个 */}
      {featuredItems.length > 0 && (
        <section className="container mx-auto max-w-6xl px-4 py-12">
          <h2 className="text-3xl font-bold text-foreground mb-8 flex items-center gap-3">
            <Star className="w-8 h-8 text-yellow-400 fill-yellow-400" />
            {t('featured')}
          </h2>
          <div className="grid md:grid-cols-2 gap-6">
            {featuredItems.map(item => (
              <Link
                key={item.slug}
                href={`/${contentType}/${item.slug}`}
                className="group relative overflow-hidden rounded-xl bg-card border border-border hover:border-[hsl(var(--nav-theme))] transition-all duration-300"
              >
                {item.frontmatter.image && (
                  <div className="relative h-48 overflow-hidden">
                    <Image
                      src={item.frontmatter.image}
                      alt={`${item.frontmatter.title} - Featured ${contentType} guide`}
                      fill
                      className="object-cover group-hover:scale-105 transition-transform duration-300"
                      unoptimized
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-card to-transparent" />
                  </div>
                )}
                <div className="p-6">
                  {item.frontmatter.category && (
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[hsl(var(--nav-theme)/0.1)] text-[hsl(var(--nav-theme-light))] text-sm mb-3">
                      {item.frontmatter.category}
                    </div>
                  )}
                  <h3 className="text-xl font-bold text-foreground mb-2 group-hover:text-[hsl(var(--nav-theme-light))] transition-colors">
                    {extractPrimaryKeyword(item.frontmatter.title)}
                  </h3>
                  <p className="text-muted-foreground mb-4">
                    {item.frontmatter.description}
                  </p>
                  <div className="flex items-center gap-4 text-sm text-muted-foreground">
                    {item.frontmatter.date && (
                      <div className="flex items-center gap-1">
                        <Calendar className="w-4 h-4" />
                        <span>{item.frontmatter.date}</span>
                      </div>
                    )}
                    {item.frontmatter.author && (
                      <div className="flex items-center gap-1">
                        <User className="w-4 h-4" />
                        <span>{item.frontmatter.author}</span>
                      </div>
                    )}
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </section>
      )}

      {/* 广告位：Featured Section 下方 - 原生横幅 */}
      <NativeBannerAd adKey={process.env.NEXT_PUBLIC_AD_NATIVE_BANNER || ''} />

      {/* 广告位 2: Featured Section 下方 - 300×250 方形 */}
      <AdBanner type="banner-300x250" />

      {/* All Items - 一行 3 个 */}
      {allItems.length > 0 && (
        <section className="container mx-auto max-w-6xl px-4 py-12">
          <h2 className="text-3xl font-bold text-foreground mb-8 flex items-center gap-3">
            <BookOpen className="w-8 h-8 text-[hsl(var(--nav-theme-light))]" />
            {t('all')}
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {allItems.map((item, index) => (
              <Fragment key={item.slug}>
                <Link
                  href={`/${contentType}/${item.slug}`}
                  className="group relative overflow-hidden rounded-xl bg-card border border-border hover:border-[hsl(var(--nav-theme))] transition-all duration-300"
                >
                  {item.frontmatter.image && (
                    <div className="relative h-32 overflow-hidden">
                      <Image
                        src={item.frontmatter.image}
                        alt={`${item.frontmatter.title} - ${contentType} guide`}
                        fill
                        className="object-cover group-hover:scale-105 transition-transform duration-300"
                        unoptimized
                      />
                      <div className="absolute inset-0 bg-gradient-to-t from-card to-transparent" />
                    </div>
                  )}
                  <div className="p-4">
                    {item.frontmatter.category && (
                      <div className="inline-flex items-center gap-2 px-2 py-1 rounded-full bg-[hsl(var(--nav-theme)/0.1)] text-[hsl(var(--nav-theme-light))] text-xs mb-2">
                        {item.frontmatter.category}
                      </div>
                    )}
                    <h3 className="text-base font-bold text-foreground mb-1 group-hover:text-[hsl(var(--nav-theme-light))] transition-colors">
                      {extractPrimaryKeyword(item.frontmatter.title)}
                    </h3>
                    <p className="text-sm text-muted-foreground line-clamp-2">
                      {item.frontmatter.description}
                    </p>
                  </div>
                </Link>
                {/* 广告位 3: All Items 中间 - 原生横幅（在第 6 个卡片之后） */}
                {index === 5 && (
                  <div className="col-span-1 sm:col-span-2 lg:col-span-3">
                    <NativeBannerAd adKey={process.env.NEXT_PUBLIC_AD_NATIVE_BANNER || ''} />
                  </div>
                )}
              </Fragment>
            ))}
          </div>
        </section>
      )}

      {/* 广告位 4: 页面底部 - 728×90 横幅 */}
      <AdBanner type="banner-728x90" />
    </div>
  )
}

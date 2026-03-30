import { notFound, redirect } from 'next/navigation'
import { getTranslations } from 'next-intl/server'
import {
  getAllContentPaths,
  getAllContent,
  isValidContentType,
  CONTENT_TYPES,
  type ContentType,
  type Language,
  type ContentFrontmatter,
} from '@/lib/content'
import { NavigationPage } from '@/components/content/NavigationPage'
import { DetailPage } from '@/components/content/DetailPage'
import { ArticleStructuredData } from '@/components/content/ArticleStructuredData'
import { ListStructuredData } from '@/components/content/ListStructuredData'
import { routing, type Locale } from '@/i18n/routing'
import { buildLanguageAlternates } from '@/lib/i18n-utils'
import type { Metadata } from 'next'

interface PageProps {
  params: Promise<{ locale: string; slug: string[] }>
}

export default async function UnifiedContentPage({ params }: PageProps) {
  const { locale, slug } = await params

  // 验证内容类型
  const contentType = slug[0]
  if (!isValidContentType(contentType)) {
    notFound()
  }

  const isListPage = slug.length === 1

  if (isListPage) {
    // 渲染列表页
    return renderListPage(contentType, locale as Language)
  } else {
    // 渲染详情页
    const slugPath = slug.slice(1)
    return renderDetailPage(contentType, slugPath, locale as Language)
  }
}

/**
 * 渲染列表页
 */
async function renderListPage(contentType: ContentType, locale: Language) {
  const items = await getAllContent(contentType, locale)

  // 如果只有一篇文章，直接跳转到详情页
  if (items.length === 1) {
    const singleArticle = items[0]
    const detailPath = `/${contentType}/${singleArticle.slug}`
    const fullPath = locale === 'en' ? detailPath : `/${locale}${detailPath}`
    redirect(fullPath)
  }

  const t = await getTranslations(`pages.${contentType}`)

  try {
    return (
      <>
        <ListStructuredData
          contentType={contentType}
          locale={locale}
          items={items}
        />
        <NavigationPage
          title={t('title')}
          description={t('description')}
          items={items}
          contentType={contentType}
          language={locale}
        />
      </>
    )
  } catch (error) {
    // 如果翻译不存在，使用默认值
    const defaultTitle = contentType.charAt(0).toUpperCase() + contentType.slice(1)

    return (
      <>
        <ListStructuredData
          contentType={contentType}
          locale={locale}
          items={items}
        />
        <NavigationPage
          title={defaultTitle}
          description={`Browse all ${contentType} content`}
          items={items}
          contentType={contentType}
          language={locale}
        />
      </>
    )
  }
}

/**
 * 渲染详情页
 */
async function renderDetailPage(
  contentType: ContentType,
  slugPath: string[],
  locale: Language
) {
  const currentSlug = slugPath.join('/')

  // 动态导入 MDX，同时获取 metadata 和内容组件
  try {
    const { default: MDXContent, metadata } = await import(
      `../../../../content/${locale}/${contentType}/${currentSlug}.mdx`
    )

    // 获取相关文章
    const allContent = await getAllContent(contentType, locale)
    const relatedArticles = allContent
      .filter(item => item.slug !== currentSlug)
      .slice(0, 3)

    return (
      <>
        <ArticleStructuredData
          frontmatter={metadata as ContentFrontmatter}
          contentType={contentType}
          locale={locale}
          slug={currentSlug}
        />
        <DetailPage
          frontmatter={metadata as ContentFrontmatter}
          content={<MDXContent />}
          contentType={contentType}
          language={locale}
          currentSlug={currentSlug}
          relatedArticles={relatedArticles}
        />
      </>
    )
  } catch {
    // 如果当前语言的 MDX 不存在，尝试加载英文版本
    if (locale !== 'en') {
      try {
        const { default: MDXContent, metadata } = await import(
          `../../../../content/en/${contentType}/${currentSlug}.mdx`
        )

        const allContent = await getAllContent(contentType, locale)
        const relatedArticles = allContent
          .filter(item => item.slug !== currentSlug)
          .slice(0, 3)

        return (
          <>
            <ArticleStructuredData
              frontmatter={metadata as ContentFrontmatter}
              contentType={contentType}
              locale={locale}
              slug={currentSlug}
            />
            <DetailPage
              frontmatter={metadata as ContentFrontmatter}
              content={<MDXContent />}
              contentType={contentType}
              language={locale}
              currentSlug={currentSlug}
              relatedArticles={relatedArticles}
            />
          </>
        )
      } catch {
        notFound()
      }
    }
    notFound()
  }
}

/**
 * 生成静态参数
 */
export async function generateStaticParams() {
  const allPaths = await getAllContentPaths()
  const params: { locale: string; slug: string[] }[] = []

  for (const locale of routing.locales) {
    // 添加列表页
    for (const type of CONTENT_TYPES) {
      params.push({ locale, slug: [type] })
    }

    // 添加详情页
    for (const path of allPaths) {
      params.push({ locale, slug: path })
    }
  }

  return params
}

/**
 * 生成元数据
 */
export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { locale, slug } = await params
  const contentType = slug[0]
  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || 'https://www.lucidblocks.wiki'

  if (!isValidContentType(contentType)) {
    return { title: 'Not Found' }
  }

  const isListPage = slug.length === 1

  if (isListPage) {
    // 列表页元数据
    const t = await getTranslations(`pages.${contentType}`)

    try {
      const title = t('metaTitle')
      const description = t('metaDescription')
      const path = `/${contentType}`

      return {
        title,
        description,
        alternates: buildLanguageAlternates(path, locale as Locale, siteUrl),
        openGraph: {
          title,
          description,
          url: `${siteUrl}${locale === 'en' ? path : `/${locale}${path}`}`,
        },
        robots: {
          index: true,
          follow: true,
          googleBot: {
            index: true,
            follow: true,
            'max-video-preview': -1,
            'max-image-preview': 'large',
            'max-snippet': -1,
          },
        },
      }
    } catch {
      // 如果翻译不存在，使用默认值
      const defaultTitle = `${contentType.charAt(0).toUpperCase() + contentType.slice(1)} - Lucid Blocks Wiki`
      const path = `/${contentType}`

      return {
        title: defaultTitle,
        description: `Browse all ${contentType} content for Lucid Blocks Wiki`,
        alternates: buildLanguageAlternates(path, locale as Locale, siteUrl),
        robots: {
          index: true,
          follow: true,
          googleBot: {
            index: true,
            follow: true,
            'max-video-preview': -1,
            'max-image-preview': 'large',
            'max-snippet': -1,
          },
        },
      }
    }
  } else {
    // 详情页元数据（从 MDX import 获取）
    const slugPath = slug.slice(1)
    const currentSlug = slugPath.join('/')

    try {
      const { metadata } = await import(
        `../../../../content/${locale}/${contentType}/${currentSlug}.mdx`
      )

      const fullPath = `/${slug.join('/')}`

      return {
        title: `${metadata.title} - Lucid Blocks Wiki`,
        description: metadata.description,
        alternates: buildLanguageAlternates(fullPath, locale as Locale, siteUrl),
        openGraph: {
          title: metadata.title,
          description: metadata.description,
          images: metadata.image ? [metadata.image] : [],
          url: `${siteUrl}${locale === 'en' ? fullPath : `/${locale}${fullPath}`}`,
        },
        robots: {
          index: true,
          follow: true,
          googleBot: {
            index: true,
            follow: true,
            'max-video-preview': -1,
            'max-image-preview': 'large',
            'max-snippet': -1,
          },
        },
      }
    } catch {
      // Fallback 到英文
      if (locale !== 'en') {
        try {
          const { metadata } = await import(
            `../../../../content/en/${contentType}/${currentSlug}.mdx`
          )

          const fullPath = `/${slug.join('/')}`

          return {
            title: `${metadata.title} - Lucid Blocks Wiki`,
            description: metadata.description,
            alternates: buildLanguageAlternates(fullPath, locale as Locale, siteUrl),
            openGraph: {
              title: metadata.title,
              description: metadata.description,
              images: metadata.image ? [metadata.image] : [],
              url: `${siteUrl}${locale === 'en' ? fullPath : `/${locale}${fullPath}`}`,
            },
            robots: {
              index: true,
              follow: true,
              googleBot: {
                index: true,
                follow: true,
                'max-video-preview': -1,
                'max-image-preview': 'large',
                'max-snippet': -1,
              },
            },
          }
        } catch {
          return { title: 'Not Found' }
        }
      }
      return { title: 'Not Found' }
    }
  }
}

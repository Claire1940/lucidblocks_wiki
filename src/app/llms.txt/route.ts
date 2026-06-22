import { getAllContent, CONTENT_TYPES, type ContentType } from '@/lib/content'
import { routing } from '@/i18n/routing'

// output:'export' 要求路由处理器显式声明静态
export const dynamic = 'force-static'

export async function GET() {
  const baseUrl = process.env.NEXT_PUBLIC_SITE_URL || 'https://www.lucidblocks.wiki'
  const siteName = process.env.NEXT_PUBLIC_SITE_NAME || 'Lucid Blocks Wiki'

  const lines: string[] = []
  lines.push(`# ${siteName}`)
  lines.push('')
  lines.push(`> ${siteName} is a comprehensive game wiki providing guides, tips, walkthroughs, and community resources.`)
  lines.push('')
  lines.push(`Website: ${baseUrl}`)
  lines.push(`Languages: ${routing.locales.join(', ')}`)
  lines.push('')

  for (const contentType of CONTENT_TYPES) {
    try {
      const articles = await getAllContent(contentType as ContentType, 'en')
      if (articles.length === 0) continue

      lines.push(`## ${contentType.charAt(0).toUpperCase() + contentType.slice(1)}`)
      lines.push('')
      for (const article of articles) {
        const url = `${baseUrl}/${contentType}/${article.slug}`
        const title = article.frontmatter.title || article.slug
        const desc = article.frontmatter.description ? `: ${article.frontmatter.description}` : ''
        lines.push(`- [${title}](${url})${desc}`)
      }
      lines.push('')
    } catch {
      // skip content types that fail to load
    }
  }

  return new Response(lines.join('\n'), {
    headers: {
      'Content-Type': 'text/plain; charset=utf-8',
      'Cache-Control': 'public, max-age=86400, s-maxage=86400',
    },
  })
}

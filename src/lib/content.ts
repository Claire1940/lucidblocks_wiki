import { CONTENT_TYPES as CONFIG_CONTENT_TYPES } from '@/config/navigation'
import { routing, type Locale } from '@/i18n/routing'
import contentManifest from '@/generated/content-manifest.json'

/**
 * 内容清单（构建期由 scripts/generate-content-manifest.mjs 生成并打包进 bundle）。
 *
 * 为什么用清单而不是 fs：Cloudflare Workers（OpenNext）运行时没有文件系统，原先在请求时
 * 用 fs.readdirSync 扫 content/ 目录枚举文章会扫到空，导致 sitemap/llms/分类列表页失效。
 * 改为构建期把目录扫描成静态清单，运行时只读清单 + 动态 import MDX（已被 webpack 打包），
 * 从而在边缘运行时也能正确枚举文章。本地/Docker（有 fs）行为不变。
 */
type ManifestEntry = { slug: string; file: string }
type ContentManifest = Record<string, Record<string, ManifestEntry[]>>
const MANIFEST = contentManifest as unknown as ContentManifest

/** 取某 (语言, 内容类型) 下的清单条目（slug + 真实文件名） */
function entriesFor(language: string, contentType: string): ManifestEntry[] {
  return MANIFEST[language]?.[contentType] ?? []
}

/**
 * 从 content 目录路径解析出 (语言, 内容类型)。
 * 调用方传入的 dir 形如 path.join(process.cwd(), 'content', <lang>, <type>)，
 * 边缘运行时 process.cwd() 可能为 '/'，因此按 'content' 段定位而非依赖绝对路径。
 */
function parseContentDir(dir: string): { language: string; contentType: string } | null {
  const parts = dir.split(/[\\/]/).filter(Boolean)
  const idx = parts.lastIndexOf('content')
  if (idx === -1) return null
  const language = parts[idx + 1]
  const contentType = parts[idx + 2]
  if (!language || !contentType) return null
  return { language, contentType }
}

/**
 * 根据 slug 在目录中反查真实文件名（不含 .mdx）
 * 例如 slug="lucid-blocks-guide" → 返回 "lucid:blocks-guide"
 * （改为查清单，签名保持 (dir, slug) 不变，调用方无需改动）
 */
export function findFileBySlug(dir: string, slug: string, _basePath: string[] = []): string | null {
  const parsed = parseContentDir(dir)
  if (!parsed) return null
  const entry = entriesFor(parsed.language, parsed.contentType).find((e) => e.slug === slug)
  return entry ? entry.file : null
}

// 通用 Frontmatter 接口
export interface ContentFrontmatter {
  title: string
  description: string
  category?: string
  image?: string
  date?: string
  lastModified?: string
  author?: string
  // 新增：可选的手动颜色配置
  themeColor?: string  // 十六进制颜色，如 "1e40af"
  backgroundText?: string  // 自定义背景文字
  // 扩展字段（用于不同内容类型）
  rarity?: string  // 用于 units
  type?: string    // 用于 traits
  code?: string    // 用于 codes
}

// 从统一配置导入内容类型
export const CONTENT_TYPES = CONFIG_CONTENT_TYPES
export type ContentType = typeof CONTENT_TYPES[number]

// 支持的语言（使用 routing.ts 中的 Locale 类型）
export type Language = Locale

// 内容项接口
export interface ContentItem {
  slug: string
  frontmatter: ContentFrontmatter
}

// 内容数据接口
export interface ContentData {
  content: string
  frontmatter: ContentFrontmatter
}

interface GetAllContentOptions {
  includeFallback?: boolean
}

/**
 * 获取所有内容列表（支持递归读取嵌套目录）
 * 枚举来自构建期清单；用动态 import 获取 MDX 文件的 metadata
 */
export async function getAllContent(
  contentType: ContentType,
  language: Language,
  options: GetAllContentOptions = {}
): Promise<ContentItem[]> {
  const items: ContentItem[] = []
  const { includeFallback = true } = options

  // 当前语言的真实文件名映射（slug → file），用于动态 import
  const fileBySlug = new Map<string, string>()
  for (const e of entriesFor(language, contentType)) fileBySlug.set(e.slug, e.file)

  // 英文 fallback 映射
  const enFileBySlug = new Map<string, string>()
  if (includeFallback && language !== 'en') {
    for (const e of entriesFor('en', contentType)) enFileBySlug.set(e.slug, e.file)
  }

  // 合并 slug 列表（当前语言优先，英文补充缺失的）
  const slugs = [...new Set([...fileBySlug.keys(), ...enFileBySlug.keys()])]

  for (const slug of slugs) {
    try {
      // 先尝试当前语言（用真实文件名以处理含特殊字符的文件名）
      const realFile = fileBySlug.get(slug)
      if (realFile === undefined) throw new Error('not in current locale')
      const mod = await import(`../../content/${language}/${contentType}/${realFile}.mdx`)
      items.push({
        slug,
        frontmatter: mod.metadata as ContentFrontmatter,
      })
    } catch {
      // Fallback 到英文
      if (includeFallback && language !== 'en') {
        try {
          const enRealFile = enFileBySlug.get(slug)
          if (enRealFile === undefined) continue
          const mod = await import(`../../content/en/${contentType}/${enRealFile}.mdx`)
          items.push({
            slug,
            frontmatter: mod.metadata as ContentFrontmatter,
          })
        } catch {
          // 跳过无法加载的文件
        }
      }
    }
  }

  // 按日期排序(最新的在前)
  return items.sort((a, b) => {
    // 添加 frontmatter 存在性检查(防御性编程)
    if (!a.frontmatter || !b.frontmatter) {
      console.warn('Missing frontmatter in content item:', { a: a.slug, b: b.slug })
      return 0
    }
    if (!a.frontmatter.date || !b.frontmatter.date) return 0
    return new Date(b.frontmatter.date).getTime() - new Date(a.frontmatter.date).getTime()
  })
}

/**
 * 获取所有内容路径（用于 generateStaticParams）
 * 返回格式: [['guide', 'beginner'], ['unit', 'jinwoo'], ...]
 */
export async function getAllContentPaths(language: Language = 'en'): Promise<string[][]> {
  const paths: string[][] = []

  for (const contentType of CONTENT_TYPES) {
    for (const entry of entriesFor(language, contentType)) {
      paths.push([contentType, ...entry.slug.split('/')])
    }
  }

  return paths
}

/**
 * 获取所有内容的 slug（用于 generateStaticParams）
 */
export async function getAllContentSlugs(
  contentType: ContentType,
  language: Language,
  options?: { includeFallback?: boolean }
): Promise<string[]> {
  if (options?.includeFallback === false) {
    return entriesFor(language, contentType).map((e) => e.slug)
  }

  const items = await getAllContent(contentType, language)
  return items.map(item => item.slug)
}

/**
 * 验证内容类型是否有效
 */
export function isValidContentType(type: string): type is ContentType {
  return CONTENT_TYPES.includes(type as ContentType)
}

/**
 * 验证语言是否有效
 */
export function isValidLanguage(lang: string): lang is Language {
  // 从各站 routing 配置动态取 locales，避免硬编码某站的语言导致跨站类型不匹配
  return (routing.locales as readonly string[]).includes(lang)
}

/**
 * 获取默认语言
 */
export function getDefaultLanguage(): Language {
  return routing.defaultLocale as Language
}

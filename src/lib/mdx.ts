import fs from 'fs'
import path from 'path'
import matter from 'gray-matter'
import { compileMDX } from 'next-mdx-remote/rsc'
import remarkGfm from 'remark-gfm'

// 定义 Frontmatter 类型
export interface GuideFrontmatter {
  title: string
  description: string
  category: string
  image: string
  date: string
  author?: string
}

// 定义 Guide 类型
export interface Guide {
  slug: string
  frontmatter: GuideFrontmatter
}

/**
 * 根据 slug 和语言获取单个攻略
 */
export async function getGuideBySlug(slug: string, language: string) {
  const filePath = path.join(process.cwd(), 'content', language, 'guide', `${slug}.mdx`)

  // 检查文件是否存在
  if (!fs.existsSync(filePath)) {
    throw new Error(`Guide not found: ${filePath}`)
  }

  const source = fs.readFileSync(filePath, 'utf8')
  const { content, data } = matter(source)

  // 编译 MDX
  const mdxSource = await compileMDX<GuideFrontmatter>({
    source: content,
    options: {
      parseFrontmatter: true,
      mdxOptions: {
        remarkPlugins: [remarkGfm],
        rehypePlugins: [],
      },
    },
  })

  return {
    content: mdxSource.content,
    frontmatter: data as GuideFrontmatter,
  }
}

/**
 * 获取所有攻略列表
 */
export async function getAllGuides(language: string): Promise<Guide[]> {
  const guidesDir = path.join(process.cwd(), 'content', language, 'guide')

  // 检查目录是否存在
  if (!fs.existsSync(guidesDir)) {
    return []
  }

  const files = fs.readdirSync(guidesDir).filter(f => f.endsWith('.mdx'))

  const guides = await Promise.all(
    files.map(async (file) => {
      const slug = file.replace('.mdx', '')
      const filePath = path.join(guidesDir, file)
      const source = fs.readFileSync(filePath, 'utf8')
      const { data } = matter(source)

      return {
        slug,
        frontmatter: data as GuideFrontmatter,
      }
    })
  )

  // 按日期排序（最新的在前）
  return guides.sort((a, b) => {
    return new Date(b.frontmatter.date).getTime() - new Date(a.frontmatter.date).getTime()
  })
}

/**
 * 获取所有攻略的 slug（用于 generateStaticParams）
 */
export async function getAllGuideSlugs(language: string): Promise<string[]> {
  const guidesDir = path.join(process.cwd(), 'content', language, 'guide')

  if (!fs.existsSync(guidesDir)) {
    return []
  }

  const files = fs.readdirSync(guidesDir).filter(f => f.endsWith('.mdx'))
  return files.map(file => file.replace('.mdx', ''))
}

#!/usr/bin/env node
/**
 * 构建期内容清单生成器
 *
 * 背景：Cloudflare Workers（OpenNext）运行时没有文件系统，content.ts 原先在请求时
 * 用 fs.readdirSync 扫 content/ 目录枚举文章，在 Workers 上会扫到空 → sitemap/llms/
 * 分类列表页全部失效。此脚本在构建期把 content/ 目录扫描成一份静态清单 JSON，打包进
 * worker，content.ts 改读清单而非 fs，从而在边缘运行时也能正确枚举文章。
 *
 * 输出：src/generated/content-manifest.json
 * 结构：{ [locale]: { [contentType]: Array<{ slug, file }> } }
 *   - slug：URL 用的 slug（非字母数字连字符下划线 → -，与 content.ts.fileNameToSlug 一致）
 *   - file：真实文件名相对路径（不含 .mdx），用于动态 import
 */
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const ROOT = path.resolve(__dirname, '..')
const CONTENT_DIR = path.join(ROOT, 'content')
const OUT_DIR = path.join(ROOT, 'src', 'generated')
const OUT_FILE = path.join(OUT_DIR, 'content-manifest.json')

// 必须与 src/lib/content.ts 的 fileNameToSlug 完全一致
function fileNameToSlug(fileName) {
  return fileName
    .replace(/[^a-zA-Z0-9\-_]/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '')
}

/** 递归收集某 contentType 目录下所有 .mdx，返回 { slug, file } 列表 */
function collectEntries(dir, basePath = []) {
  if (!fs.existsSync(dir)) return []
  const out = []
  const entries = fs.readdirSync(dir, { withFileTypes: true })
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name)
    if (entry.isDirectory()) {
      out.push(...collectEntries(fullPath, [...basePath, entry.name]))
    } else if (entry.name.endsWith('.mdx')) {
      const fileName = entry.name.replace('.mdx', '')
      out.push({
        slug: [...basePath, fileNameToSlug(fileName)].join('/'),
        file: [...basePath, fileName].join('/'),
      })
    }
  }
  return out
}

function main() {
  const manifest = {}
  let total = 0

  if (!fs.existsSync(CONTENT_DIR)) {
    console.error(`[content-manifest] content 目录不存在: ${CONTENT_DIR}`)
    process.exit(1)
  }

  const locales = fs
    .readdirSync(CONTENT_DIR, { withFileTypes: true })
    .filter((d) => d.isDirectory())
    .map((d) => d.name)

  for (const locale of locales) {
    const localeDir = path.join(CONTENT_DIR, locale)
    const contentTypes = fs
      .readdirSync(localeDir, { withFileTypes: true })
      .filter((d) => d.isDirectory())
      .map((d) => d.name)

    manifest[locale] = {}
    for (const contentType of contentTypes) {
      const entries = collectEntries(path.join(localeDir, contentType))
      manifest[locale][contentType] = entries
      total += entries.length
    }
  }

  fs.mkdirSync(OUT_DIR, { recursive: true })
  fs.writeFileSync(OUT_FILE, JSON.stringify(manifest, null, 2) + '\n', 'utf8')
  console.log(
    `[content-manifest] 已生成 ${path.relative(ROOT, OUT_FILE)}：${locales.length} 语言，${total} 篇内容`
  )
}

main()

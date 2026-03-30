#!/usr/bin/env node

/**
 * SEO 检查脚本
 *
 * 基于 需求/09.seo检查.md 的检查清单
 * 自动检查所有可以在本地验证的 SEO 项目
 *
 * 使用方法：
 *   bun run scripts/check-seo.js
 *   bun run scripts/check-seo.js --locale en
 *   bun run scripts/check-seo.js --verbose
 */

import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const projectRoot = path.resolve(__dirname, '..')

// 颜色输出
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
}

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`)
}

// 解析命令行参数
const args = process.argv.slice(2)
const locale = args.find(arg => arg.startsWith('--locale='))?.split('=')[1] || 'en'
const verbose = args.includes('--verbose')

// 检查结果统计
const results = {
  passed: [],
  warnings: [],
  errors: [],
}

function addResult(type, category, message, details = null) {
  results[type].push({ category, message, details })
}

// ============================================
// 1. 检查 robots.txt 和 sitemap.xml
// ============================================
function checkRobotsAndSitemap() {
  log('\n📋 检查 robots.txt 和 sitemap.xml...', 'cyan')

  // 检查 robots.txt
  const robotsPath = path.join(projectRoot, 'public', 'robots.txt')
  if (fs.existsSync(robotsPath)) {
    const content = fs.readFileSync(robotsPath, 'utf-8')
    if (content.includes('Sitemap:')) {
      addResult('passed', 'Robots', '✓ robots.txt 存在且包含 Sitemap 引用')
    } else {
      addResult('warnings', 'Robots', '⚠ robots.txt 缺少 Sitemap 引用')
    }
  } else {
    addResult('errors', 'Robots', '✗ robots.txt 不存在')
  }

  // 检查 sitemap.xml
  const sitemapPath = path.join(projectRoot, 'public', 'sitemap.xml')
  if (fs.existsSync(sitemapPath)) {
    addResult('passed', 'Sitemap', '✓ sitemap.xml 存在')
  } else {
    addResult('warnings', 'Sitemap', '⚠ sitemap.xml 不存在（Next.js 可能动态生成）')
  }
}

// ============================================
// 2. 检查翻译文件中的 SEO 元数据
// ============================================
function checkSEOMetadata() {
  log('\n🏷️  检查 SEO 元数据...', 'cyan')

  const localesDir = path.join(projectRoot, 'src', 'locales')
  const localeFile = path.join(localesDir, `${locale}.json`)

  if (!fs.existsSync(localeFile)) {
    addResult('errors', 'Metadata', `✗ 翻译文件不存在: ${locale}.json`)
    return
  }

  const translations = JSON.parse(fs.readFileSync(localeFile, 'utf-8'))
  const seo = translations.seo?.home

  if (!seo) {
    addResult('errors', 'Metadata', '✗ 缺少 seo.home 配置')
    return
  }

  // 检查 Title
  if (seo.title) {
    const titleLength = seo.title.length
    if (titleLength >= 50 && titleLength <= 60) {
      addResult('passed', 'Title', `✓ Title 长度合适 (${titleLength} 字符)`)
    } else if (titleLength < 50) {
      addResult('warnings', 'Title', `⚠ Title 过短 (${titleLength} 字符，建议 50-60)`)
    } else {
      addResult('warnings', 'Title', `⚠ Title 过长 (${titleLength} 字符，建议 50-60)`)
    }
  } else {
    addResult('errors', 'Title', '✗ 缺少 Title')
  }

  // 检查 Description
  if (seo.description) {
    const descLength = seo.description.length
    if (descLength >= 150 && descLength <= 160) {
      addResult('passed', 'Description', `✓ Description 长度合适 (${descLength} 字符)`)
    } else if (descLength < 150) {
      addResult('warnings', 'Description', `⚠ Description 过短 (${descLength} 字符，建议 150-160)`)
    } else {
      addResult('warnings', 'Description', `⚠ Description 过长 (${descLength} 字符，建议 150-160)`)
    }
  } else {
    addResult('errors', 'Description', '✗ 缺少 Description')
  }

  // 检查 Keywords
  if (seo.keywords) {
    const keywords = seo.keywords.split(',').map(k => k.trim()).filter(k => k)
    if (keywords.length >= 5 && keywords.length <= 10) {
      addResult('passed', 'Keywords', `✓ Keywords 数量合适 (${keywords.length} 个)`)
    } else if (keywords.length < 5) {
      addResult('warnings', 'Keywords', `⚠ Keywords 过少 (${keywords.length} 个，建议 5-10)`)
    } else {
      addResult('warnings', 'Keywords', `⚠ Keywords 过多 (${keywords.length} 个，建议 5-10)`)
    }
  } else {
    addResult('warnings', 'Keywords', '⚠ 缺少 Keywords（非必须，但建议添加）')
  }

  // 检查 Open Graph
  if (seo.ogTitle && seo.ogDescription) {
    addResult('passed', 'OpenGraph', '✓ Open Graph 元数据完整')
  } else {
    addResult('warnings', 'OpenGraph', '⚠ Open Graph 元数据不完整')
  }

  // 检查 Twitter Card
  if (seo.twitterTitle && seo.twitterDescription) {
    addResult('passed', 'Twitter', '✓ Twitter Card 元数据完整')
  } else {
    addResult('warnings', 'Twitter', '⚠ Twitter Card 元数据不完整')
  }
}

// ============================================
// 3. 检查图片资源
// ============================================
function checkImages() {
  log('\n🖼️  检查图片资源...', 'cyan')

  const publicDir = path.join(projectRoot, 'public')

  // 检查 OG Image
  const ogImagePath = path.join(publicDir, 'og-image.jpg')
  if (fs.existsSync(ogImagePath)) {
    const stats = fs.statSync(ogImagePath)
    const sizeKB = (stats.size / 1024).toFixed(2)
    addResult('passed', 'Images', `✓ og-image.jpg 存在 (${sizeKB} KB)`)
  } else {
    addResult('errors', 'Images', '✗ og-image.jpg 不存在')
  }

  // 检查 Favicon
  const faviconFiles = ['favicon.ico', 'favicon-16x16.png', 'favicon-32x32.png', 'apple-touch-icon.png']
  const missingFavicons = faviconFiles.filter(file => !fs.existsSync(path.join(publicDir, file)))

  if (missingFavicons.length === 0) {
    addResult('passed', 'Favicon', '✓ 所有 Favicon 文件存在')
  } else {
    addResult('warnings', 'Favicon', `⚠ 缺少 Favicon 文件: ${missingFavicons.join(', ')}`)
  }
}

// ============================================
// 4. 检查多语言配置 (Hreflangs)
// ============================================
function checkHreflangs() {
  log('\n🌍 检查多语言配置...', 'cyan')

  const localesDir = path.join(projectRoot, 'src', 'locales')
  const localeFiles = fs.readdirSync(localesDir).filter(f => f.endsWith('.json'))

  if (localeFiles.length > 1) {
    addResult('passed', 'Hreflangs', `✓ 支持 ${localeFiles.length} 种语言`)

    // 检查 i18n 配置
    const i18nRoutingPath = path.join(projectRoot, 'src', 'i18n', 'routing.ts')
    if (fs.existsSync(i18nRoutingPath)) {
      addResult('passed', 'Hreflangs', '✓ i18n routing 配置存在')
    } else {
      addResult('warnings', 'Hreflangs', '⚠ i18n routing 配置不存在')
    }
  } else {
    addResult('warnings', 'Hreflangs', '⚠ 只有单语言，建议添加多语言支持')
  }
}

// ============================================
// 5. 检查结构化数据 (JSON-LD)
// ============================================
function checkStructuredData() {
  log('\n📊 检查结构化数据...', 'cyan')

  // 检查是否有 JSON-LD 配置
  const layoutPath = path.join(projectRoot, 'src', 'app', '[locale]', 'layout.tsx')
  if (fs.existsSync(layoutPath)) {
    const content = fs.readFileSync(layoutPath, 'utf-8')

    // 检查是否有 Organization schema
    if (content.includes('Organization') || content.includes('WebSite')) {
      addResult('passed', 'Structured', '✓ 包含结构化数据配置')
    } else {
      addResult('warnings', 'Structured', '⚠ 未找到结构化数据（建议添加 Organization/WebSite schema）')
    }
  }
}

// ============================================
// 6. 检查页面内容结构
// ============================================
function checkPageStructure() {
  log('\n📄 检查页面结构...', 'cyan')

  const localeFile = path.join(projectRoot, 'src', 'locales', `${locale}.json`)
  if (!fs.existsSync(localeFile)) {
    return
  }

  const translations = JSON.parse(fs.readFileSync(localeFile, 'utf-8'))

  // 检查 Hero 部分
  if (translations.hero?.title && translations.hero?.description) {
    addResult('passed', 'Content', '✓ Hero 部分内容完整')
  } else {
    addResult('warnings', 'Content', '⚠ Hero 部分内容不完整')
  }

  // 检查 FAQ
  if (translations.faq?.items && translations.faq.items.length > 0) {
    addResult('passed', 'Content', `✓ FAQ 包含 ${translations.faq.items.length} 个问题`)
  } else {
    addResult('warnings', 'Content', '⚠ 缺少 FAQ 内容')
  }

  // 检查工具/资源
  if (translations.tools?.items && translations.tools.items.length > 0) {
    addResult('passed', 'Content', `✓ 工具/资源包含 ${translations.tools.items.length} 个项目`)
  } else {
    addResult('warnings', 'Content', '⚠ 缺少工具/资源内容')
  }
}

// ============================================
// 7. 检查配置文件
// ============================================
function checkConfigFiles() {
  log('\n⚙️  检查配置文件...', 'cyan')

  // 检查 next.config.js
  const nextConfigPath = path.join(projectRoot, 'next.config.ts')
  if (fs.existsSync(nextConfigPath)) {
    const content = fs.readFileSync(nextConfigPath, 'utf-8')

    // 检查是否配置了图片域名
    if (content.includes('remotePatterns') || content.includes('domains')) {
      addResult('passed', 'Config', '✓ Next.js 图片域名已配置')
    } else {
      addResult('warnings', 'Config', '⚠ Next.js 未配置图片域名')
    }
  }

  // 检查 manifest.json
  const manifestPath = path.join(projectRoot, 'public', 'manifest.json')
  if (fs.existsSync(manifestPath)) {
    addResult('passed', 'Config', '✓ manifest.json 存在')
  } else {
    addResult('warnings', 'Config', '⚠ manifest.json 不存在')
  }
}

// ============================================
// 主函数
// ============================================
async function main() {
  log('='.repeat(60), 'blue')
  log('🔍 SEO 检查工具', 'blue')
  log('='.repeat(60), 'blue')
  log(`检查语言: ${locale}`, 'cyan')

  try {
    checkRobotsAndSitemap()
    checkSEOMetadata()
    checkImages()
    checkHreflangs()
    checkStructuredData()
    checkPageStructure()
    checkConfigFiles()

    // 输出结果
    log('\n' + '='.repeat(60), 'blue')
    log('📊 检查结果汇总', 'blue')
    log('='.repeat(60), 'blue')

    // 通过的检查
    if (results.passed.length > 0) {
      log(`\n✅ 通过 (${results.passed.length})`, 'green')
      results.passed.forEach(({ category, message }) => {
        log(`  [${category}] ${message}`, 'green')
      })
    }

    // 警告
    if (results.warnings.length > 0) {
      log(`\n⚠️  警告 (${results.warnings.length})`, 'yellow')
      results.warnings.forEach(({ category, message }) => {
        log(`  [${category}] ${message}`, 'yellow')
      })
    }

    // 错误
    if (results.errors.length > 0) {
      log(`\n❌ 错误 (${results.errors.length})`, 'red')
      results.errors.forEach(({ category, message }) => {
        log(`  [${category}] ${message}`, 'red')
      })
    }

    // 总结
    log('\n' + '='.repeat(60), 'blue')
    const total = results.passed.length + results.warnings.length + results.errors.length
    const score = ((results.passed.length / total) * 100).toFixed(1)
    log(`总分: ${score}% (${results.passed.length}/${total})`, score >= 80 ? 'green' : score >= 60 ? 'yellow' : 'red')

    // 建议
    log('\n💡 建议:', 'cyan')
    log('  1. 优先修复所有 ❌ 错误项', 'cyan')
    log('  2. 然后处理 ⚠️  警告项', 'cyan')
    log('  3. 使用 AITDK 插件检查以下项目:', 'cyan')
    log('     - SERP 展现形态（缩略图、站点名）', 'cyan')
    log('     - PageSpeed / Core Web Vitals', 'cyan')
    log('     - Traffic 数据和竞品分析', 'cyan')

    log('\n' + '='.repeat(60), 'blue')

    // 退出码
    process.exit(results.errors.length > 0 ? 1 : 0)

  } catch (error) {
    log(`\n❌ 检查失败: ${error.message}`, 'red')
    if (verbose) {
      console.error(error)
    }
    process.exit(1)
  }
}

main()

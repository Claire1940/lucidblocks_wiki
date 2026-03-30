#!/usr/bin/env node
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

/**
 * 验证翻译文件中的图标是否都已在 iconRegistry 中注册
 */
async function validateIcons() {
  console.log('🔍 Validating icon usage...\n')

  // 1. 读取图标注册表
  const registryPath = path.join(__dirname, '../src/lib/iconRegistry.ts')
  const registryContent = fs.readFileSync(registryPath, 'utf-8')

  // 提取已注册的图标名称（简单正则匹配）
  const registeredIcons = new Set()
  const iconMatches = registryContent.matchAll(/(\w+):\s*LucideIcons\.\1/g)
  for (const match of iconMatches) {
    registeredIcons.add(match[1])
  }

  console.log(`✅ Found ${registeredIcons.size} registered icons`)

  // 2. 只读取英文翻译文件（图标名称应该是代码标识符，不应被翻译）
  const localesDir = path.join(__dirname, '../src/locales')
  const enFilePath = path.join(localesDir, 'en.json')

  if (!fs.existsSync(enFilePath)) {
    console.error('❌ en.json not found!')
    process.exit(1)
  }

  const usedIcons = new Set()
  const iconUsageByFile = new Map()

  const content = JSON.parse(fs.readFileSync(enFilePath, 'utf-8'))
  const file = 'en.json'

  // 只处理英文文件
  {

  // 提取 tools.cards 中的图标
  if (content.tools?.cards) {
    content.tools.cards.forEach(card => {
      if (card.icon) {
        usedIcons.add(card.icon)
        if (!iconUsageByFile.has(card.icon)) {
          iconUsageByFile.set(card.icon, [])
        }
        iconUsageByFile.get(card.icon).push(`${file}:tools.cards`)
      }
    })
  }

  // 提取 coopGuide.roles 中的图标
  if (content.coopGuide?.roles) {
    content.coopGuide.roles.forEach(role => {
      if (role.icon) {
        usedIcons.add(role.icon)
        if (!iconUsageByFile.has(role.icon)) {
          iconUsageByFile.set(role.icon, [])
        }
        iconUsageByFile.get(role.icon).push(`${file}:coopGuide.roles`)
      }
    })
  }

  // 提取 beginnerGuide.pitfalls 中的图标
  if (content.beginnerGuide?.pitfalls) {
    content.beginnerGuide.pitfalls.forEach(pitfall => {
      if (pitfall.icon) {
        usedIcons.add(pitfall.icon)
        if (!iconUsageByFile.has(pitfall.icon)) {
          iconUsageByFile.set(pitfall.icon, [])
        }
        iconUsageByFile.get(pitfall.icon).push(`${file}:beginnerGuide.pitfalls`)
      }
    })
  }
  }

  console.log(`✅ Found ${usedIcons.size} icons used in translation files\n`)

  // 3. 检查缺失的图标
  const missingIcons = [...usedIcons].filter(icon => !registeredIcons.has(icon))

  if (missingIcons.length > 0) {
    console.error('❌ Missing icons in iconRegistry.ts:\n')
    missingIcons.forEach(icon => {
      const locations = iconUsageByFile.get(icon) || []
      console.error(`  - ${icon}`)
      locations.forEach(loc => console.error(`    Used in: ${loc}`))
    })
    console.error('\n💡 Add these icons to src/lib/iconRegistry.ts:\n')
    missingIcons.forEach(icon => {
      console.error(`  ${icon}: LucideIcons.${icon},`)
    })
    process.exit(1)
  }

  // 4. 检查未使用的图标（可选警告）
  const unusedIcons = [...registeredIcons].filter(icon =>
    !usedIcons.has(icon) && icon !== 'HelpCircle'
  )

  if (unusedIcons.length > 0) {
    console.warn('⚠️  Registered but unused icons (consider removing):\n')
    unusedIcons.forEach(icon => console.warn(`  - ${icon}`))
    console.warn('')
  }

  console.log('✅ All icons are properly registered!\n')
}

validateIcons().catch(err => {
  console.error('❌ Validation failed:', err)
  process.exit(1)
})

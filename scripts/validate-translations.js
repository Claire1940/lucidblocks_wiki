#!/usr/bin/env node

/**
 * 验证所有翻译文件
 *
 * 用法：
 *   node scripts/validate-translations.js
 *
 * 在构建时自动运行，确保所有翻译文件符合 schema
 */

import { readFileSync, readdirSync } from 'fs'
import { join, dirname } from 'path'
import { fileURLToPath } from 'url'
import { validateTranslations } from '../src/lib/translationSchema.ts'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

const LOCALES_DIR = join(__dirname, '../src/locales')

console.log('🔍 Validating translation files...\n')

let hasErrors = false
const results = []

try {
  // 读取所有 locale 文件
  const files = readdirSync(LOCALES_DIR).filter(f => f.endsWith('.json'))

  for (const file of files) {
    const locale = file.replace('.json', '')
    const filePath = join(LOCALES_DIR, file)

    console.log(`📄 Checking ${file}...`)

    try {
      const content = readFileSync(filePath, 'utf-8')
      const data = JSON.parse(content)

      const result = validateTranslations(data, locale)

      if (result.success) {
        console.log(`  ✅ Valid\n`)
        results.push({ locale, status: 'valid' })
      } else {
        console.log(`  ❌ Invalid\n`)
        hasErrors = true
        results.push({ locale, status: 'invalid', errors: result.error.issues })
      }
    } catch (error) {
      console.error(`  ❌ Error reading or parsing file:`, error.message)
      hasErrors = true
      results.push({ locale, status: 'error', error: error.message })
    }
  }

  // 打印总结
  console.log('\n' + '='.repeat(50))
  console.log('📊 Validation Summary')
  console.log('='.repeat(50))

  const valid = results.filter(r => r.status === 'valid').length
  const invalid = results.filter(r => r.status === 'invalid').length
  const errors = results.filter(r => r.status === 'error').length

  console.log(`✅ Valid: ${valid}`)
  console.log(`❌ Invalid: ${invalid}`)
  console.log(`⚠️  Errors: ${errors}`)
  console.log(`📁 Total: ${results.length}`)

  if (hasErrors) {
    console.log('\n❌ Validation failed! Please fix the errors above.')
    process.exit(1)
  } else {
    console.log('\n✅ All translation files are valid!')
    process.exit(0)
  }
} catch (error) {
  console.error('❌ Fatal error:', error)
  process.exit(1)
}

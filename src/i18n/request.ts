import { getRequestConfig } from 'next-intl/server'
import { routing, type Locale } from './routing'
import deepMerge from 'deepmerge'

// 静态导入所有翻译文件
import enMessages from '@/locales/en.json'
import ruMessages from '@/locales/ru.json'
import ptMessages from '@/locales/pt.json'
import deMessages from '@/locales/de.json'
import esMessages from '@/locales/es.json'
import jaMessages from '@/locales/ja.json'
import trMessages from '@/locales/tr.json'
import frMessages from '@/locales/fr.json'

const messages: Record<string, any> = {
	en: enMessages,
	ru: ruMessages,
	pt: ptMessages,
	de: deMessages,
	es: esMessages,
	ja: jaMessages,
	tr: trMessages,
	fr: frMessages,
}

export default getRequestConfig(async ({ requestLocale }) => {
	let locale = await requestLocale

	// 使用 routing.locales 动态验证（无需硬编码类型）
	if (!locale || !routing.locales.includes(locale as Locale)) {
		locale = routing.defaultLocale
	}

	if (locale === 'en') {
		return { locale, messages: enMessages }
	}

	// 加载目标语言的翻译，并与英文深度合并（作为 fallback）
	const localeMessages = messages[locale] || enMessages
	const mergedMessages = deepMerge(enMessages, localeMessages, {
		// 数组替换而不是合并（避免重复）
		arrayMerge: (_destinationArray, sourceArray) => sourceArray,
	})

	return { locale, messages: mergedMessages }
})

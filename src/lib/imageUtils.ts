/**
 * 从 placehold.co URL 提取颜色和文字
 * 示例: https://placehold.co/800x400/1e40af/fff?text=Beginner+Guide
 */
export interface ImageMetadata {
	backgroundColor: string // 十六进制颜色，如 "1e40af"
	textColor: string // 十六进制颜色，如 "fff"
	text: string // 背景文字，如 "Beginner Guide"
}

export function extractPlaceholderMetadata(imageUrl: string): ImageMetadata | null {
	try {
		// 匹配 placehold.co URL 格式
		// https://placehold.co/WIDTHxHEIGHT/BGCOLOR/TEXTCOLOR?text=TEXT
		const placeholderRegex = /placehold\.co\/\d+x\d+\/([a-fA-F0-9]{3,6})\/([a-fA-F0-9]{3,6})\?text=([^&]+)/
		const match = imageUrl.match(placeholderRegex)

		if (!match) {
			return null
		}

		const [, bgColor, textColor, encodedText] = match

		return {
			backgroundColor: bgColor,
			textColor: textColor,
			text: decodeURIComponent(encodedText.replace(/\+/g, ' ')),
		}
	} catch (error) {
		console.error('Failed to extract placeholder metadata:', error)
		return null
	}
}

/**
 * 将十六进制颜色转换为 RGB
 */
export function hexToRgb(hex: string): { r: number; g: number; b: number } | null {
	// 移除 # 号（如果有）
	hex = hex.replace(/^#/, '')

	// 处理 3 位和 6 位十六进制
	if (hex.length === 3) {
		hex = hex
			.split('')
			.map((char) => char + char)
			.join('')
	}

	if (hex.length !== 6) {
		return null
	}

	const r = parseInt(hex.substring(0, 2), 16)
	const g = parseInt(hex.substring(2, 4), 16)
	const b = parseInt(hex.substring(4, 6), 16)

	return { r, g, b }
}

/**
 * 生成 Tailwind 兼容的 RGB 颜色字符串
 * 用于 CSS 变量或内联样式
 */
export function getTailwindRgbString(hex: string): string {
	const rgb = hexToRgb(hex)
	if (!rgb) {
		return '59 130 246' // 默认 blue-500
	}
	return `${rgb.r} ${rgb.g} ${rgb.b}`
}

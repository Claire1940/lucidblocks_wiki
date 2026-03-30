'use client'

import { Moon, Sun } from 'lucide-react'
import { useTheme } from 'next-themes'
import { useEffect, useState } from 'react'
import { useTranslations } from 'next-intl'

export function ThemeToggle() {
	const { theme, setTheme } = useTheme()
	const [mounted, setMounted] = useState(false)
	const t = useTranslations()

	// 避免水合错误
	useEffect(() => {
		setMounted(true)
	}, [])

	if (!mounted) {
		return (
			<button
				className="flex items-center gap-2 px-3 py-2 rounded-lg bg-white/5 border border-border"
				disabled
			>
				<div className="w-4 h-4" />
			</button>
		)
	}

	return (
		<button
			onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
			className="flex items-center gap-2 px-3 py-2 rounded-lg bg-white/5 hover:bg-white/10 transition border border-border"
			title={theme === 'dark' ? t('common.lightMode') : t('common.darkMode')}
			aria-label={theme === 'dark' ? t('common.lightMode') : t('common.darkMode')}
		>
			{theme === 'dark' ? (
				<Sun className="w-4 h-4" />
			) : (
				<Moon className="w-4 h-4" />
			)}
		</button>
	)
}

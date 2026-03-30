'use client'

import { useTranslations } from 'next-intl'
import { Link } from '@/i18n/navigation'

export default function NotFound() {
	const t = useTranslations('common')

	return (
		<div className="min-h-screen bg-background flex items-center justify-center px-4">
			<div className="text-center">
				<h1 className="text-6xl font-bold text-white mb-4">404</h1>
				<h2 className="text-2xl font-semibold text-slate-300 mb-4">{t('notFound')}</h2>
				<p className="text-slate-400 mb-8">{t('notFoundDescription')}</p>
				<Link
					href="/"
					className="inline-block px-6 py-3 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors"
				>
					{t('backToHome')}
				</Link>
			</div>
		</div>
	)
}

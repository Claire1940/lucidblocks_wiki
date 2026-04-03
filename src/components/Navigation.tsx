'use client'

import { Link, usePathname, useRouter } from '@/i18n/navigation'
import { Button } from '@/components/ui/button'
import { useTranslations, useLocale } from 'next-intl'
import { Globe, Menu, X, ChevronDown, ChevronRight, ExternalLink } from 'lucide-react'
import { useState, useRef, useEffect, useCallback } from 'react'
import { routing, type Locale } from '@/i18n/routing'
import { ThemeToggle } from '@/components/ThemeToggle'
import { NAVIGATION_CONFIG } from '@/config/navigation'
import { getLanguageDisplayNames } from '@/lib/i18n-utils'
import { extractPrimaryKeyword } from '@/lib/utils'
import type { NavPreviewData, NavPreviewArticle } from '@/types/nav-preview'
import type { WikiLink } from '@/lib/wiki-links'

function getRandomArticles(articles: NavPreviewArticle[], count: number): NavPreviewArticle[] {
	const copy = [...articles]
	for (let i = copy.length - 1; i > 0; i--) {
		const j = Math.floor(Math.random() * (i + 1))
		;[copy[i], copy[j]] = [copy[j], copy[i]]
	}
	return copy.slice(0, count)
}

interface NavigationProps {
	navPreviewData: NavPreviewData
	wikiLinks: WikiLink[]
}

export default function Navigation({ navPreviewData, wikiLinks }: NavigationProps) {
	const t = useTranslations()
	const locale = useLocale() as Locale
	const router = useRouter()
	const pathname = usePathname()
	const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
	const [langMenuOpen, setLangMenuOpen] = useState(false)
	const [openDropdown, setOpenDropdown] = useState<string | null>(null)
	const [mobileExpandedItem, setMobileExpandedItem] = useState<string | null>(null)
	const [wikiMenuOpen, setWikiMenuOpen] = useState(false)
	const [mobileWikiExpanded, setMobileWikiExpanded] = useState(false)
	const [randomArticles, setRandomArticles] = useState<NavPreviewArticle[]>([])
	const [mobileRandomArticles, setMobileRandomArticles] = useState<NavPreviewArticle[]>([])
	const langDropdownRef = useRef<HTMLDivElement>(null)
	const navDropdownRef = useRef<HTMLDivElement>(null)
	const wikiDropdownRef = useRef<HTMLDivElement>(null)

	// 动态获取语言显示名称
	const languageNames = getLanguageDisplayNames()

	// 点击外部关闭下拉菜单
	useEffect(() => {
		const handleClickOutside = (event: MouseEvent) => {
			if (langDropdownRef.current && !langDropdownRef.current.contains(event.target as Node)) {
				setLangMenuOpen(false)
			}
			if (navDropdownRef.current && !navDropdownRef.current.contains(event.target as Node)) {
				setOpenDropdown(null)
			}
			if (wikiDropdownRef.current && !wikiDropdownRef.current.contains(event.target as Node)) {
				setWikiMenuOpen(false)
			}
		}
		document.addEventListener('mousedown', handleClickOutside)
		return () => document.removeEventListener('mousedown', handleClickOutside)
	}, [])

	// 语言切换函数
	const switchLanguage = (newLocale: Locale) => {
		if (newLocale === locale) {
			setLangMenuOpen(false)
			return
		}
		router.replace(pathname, { locale: newLocale })
		setLangMenuOpen(false)
	}

	// 桌面端：切换导航下拉
	const toggleDesktopDropdown = useCallback((contentType: string) => {
		if (openDropdown === contentType) {
			setOpenDropdown(null)
		} else {
			const articles = navPreviewData[contentType] || []
			setRandomArticles(getRandomArticles(articles, 5))
			setOpenDropdown(contentType)
		}
	}, [openDropdown, navPreviewData])

	// 移动端：切换导航展开
	const toggleMobileExpand = useCallback((contentType: string) => {
		if (mobileExpandedItem === contentType) {
			setMobileExpandedItem(null)
		} else {
			const articles = navPreviewData[contentType] || []
			setMobileRandomArticles(getRandomArticles(articles, 5))
			setMobileExpandedItem(contentType)
		}
	}, [mobileExpandedItem, navPreviewData])

	// 从配置生成导航链接
	const navLinks = NAVIGATION_CONFIG.map(item => ({
		href: item.path,
		key: item.path.slice(1),
		label: t(`nav.${item.key}`),
		icon: item.icon
	}))

	return (
		<nav className="fixed top-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-lg border-b border-border">
			<div className="container mx-auto px-4 py-4">
				<div className="flex items-center justify-between">
					{/* Logo */}
					<Link
						href="/"
						className="flex items-center space-x-2 hover:opacity-80 transition"
					>
						<div className="w-10 h-10 bg-[hsl(var(--nav-theme))] rounded-lg flex items-center justify-center font-bold text-xl">
							L
						</div>
						<span className="font-bold text-lg hidden sm:inline">Lucid Blocks</span>
						<span className="font-bold text-lg sm:hidden">LB</span>
					</Link>

					{/* Desktop Navigation */}
					<div className="hidden md:flex items-center space-x-6 text-sm" ref={navDropdownRef}>
						{navLinks.map((link) => {
							const Icon = link.icon
							const articles = navPreviewData[link.key] || []
							const isOpen = openDropdown === link.key
							return (
								<div key={link.href} className="relative">
									<button
										onClick={() => toggleDesktopDropdown(link.key)}
										className={`flex items-center gap-2 transition ${
											isOpen ? 'text-[hsl(var(--nav-theme-light))]' : 'hover:text-[hsl(var(--nav-theme-light))]'
										}`}
									>
										<Icon className="w-4 h-4" />
										<span className="text-xs">{link.label}</span>
										<ChevronDown className={`w-3 h-3 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
									</button>
									{isOpen && (
										<div className="absolute left-1/2 -translate-x-1/2 mt-4 w-72 bg-card rounded-lg shadow-lg border border-border z-50 overflow-hidden">
											<div className="py-2">
												{randomArticles.map((article) => (
													<Link
														key={article.slug}
														href={`/${link.key}/${article.slug}`}
														className="flex items-center gap-2 px-4 py-2.5 hover:bg-white/10 transition-colors text-sm text-foreground"
														onClick={() => setOpenDropdown(null)}
													>
														<ChevronRight className="w-3 h-3 text-[hsl(var(--nav-theme-light))] flex-shrink-0" />
														<span>{extractPrimaryKeyword(article.title)}</span>
													</Link>
												))}
												{randomArticles.length === 0 && (
													<div className="px-4 py-3 text-sm text-muted-foreground text-center">
														No articles yet
													</div>
												)}
											</div>
											{articles.length > 1 && (
												<Link
													href={link.href}
													className="flex items-center justify-center gap-1 px-4 py-2.5 border-t border-border text-sm font-medium text-[hsl(var(--nav-theme-light))] hover:bg-white/5 transition-colors"
													onClick={() => setOpenDropdown(null)}
												>
													{t('common.readMore')}
													<ChevronRight className="w-3.5 h-3.5" />
												</Link>
											)}
										</div>
									)}
								</div>
							)
						})}
					</div>

					{/* Actions */}
					<div className="flex items-center gap-3">
						{/* Theme Toggle */}
						<ThemeToggle />

						{/* Language Switcher Dropdown */}
						<div className="relative" ref={langDropdownRef}>
							<button
								onClick={() => setLangMenuOpen(!langMenuOpen)}
								className="flex items-center gap-2 px-3 py-2 rounded-lg bg-white/5 hover:bg-white/10 transition border border-border"
								title={t('common.switchLanguage')}
								aria-expanded={langMenuOpen}
								aria-haspopup="listbox"
							>
								<Globe className="w-4 h-4" />
								<span className="text-sm font-medium hidden sm:inline">
									{languageNames[locale]}
								</span>
								<ChevronDown className={`w-3 h-3 transition-transform ${langMenuOpen ? 'rotate-180' : ''}`} />
							</button>

							{langMenuOpen && (
								<div
									className="absolute right-0 mt-2 py-1 w-32 bg-card rounded-lg shadow-lg border border-border z-50"
									role="listbox"
									aria-label="Select language"
								>
									{routing.locales.map((loc) => (
										<button
											key={loc}
											onClick={() => switchLanguage(loc)}
											className={`w-full px-4 py-2 text-left text-sm hover:bg-white/10 transition-colors ${
												loc === locale ? 'text-[hsl(var(--nav-theme-light))] font-semibold' : 'text-foreground'
											}`}
											role="option"
											aria-selected={loc === locale}
										>
											{languageNames[loc]}
										</button>
									))}
								</div>
							)}
						</div>

						{/* More Wikis Dropdown */}
						<div className="relative hidden sm:block" ref={wikiDropdownRef}>
							<Button
								size="sm"
								onClick={() => setWikiMenuOpen(!wikiMenuOpen)}
								className="bg-[hsl(var(--nav-theme))] hover:bg-[hsl(var(--nav-theme)/0.9)] text-white text-xs px-2.5 py-1 h-7"
								aria-expanded={wikiMenuOpen}
								aria-haspopup="menu"
							>
								More Wikis
								<ChevronDown className={`w-3 h-3 ml-1 transition-transform ${wikiMenuOpen ? 'rotate-180' : ''}`} />
							</Button>

							{wikiMenuOpen && (
								<div
									className="absolute right-0 mt-2 py-1 w-72 bg-card rounded-lg shadow-lg border border-border z-50"
									role="menu"
								>
									{wikiLinks.map((wiki) => (
										<a
											key={wiki.url}
											href={wiki.url}
											target="_blank"
											rel="noopener noreferrer"
											className="flex items-center gap-2 px-4 py-2.5 hover:bg-white/10 transition-colors text-sm text-foreground"
											role="menuitem"
											onClick={() => setWikiMenuOpen(false)}
										>
											<ExternalLink className="w-3.5 h-3.5 text-[hsl(var(--nav-theme-light))] flex-shrink-0" />
											<span className="line-clamp-1">{wiki.name}</span>
										</a>
									))}
								</div>
							)}
						</div>

						{/* Mobile Menu Toggle */}
						<button
							onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
							className="md:hidden p-2 hover:bg-white/10 rounded-lg transition"
						>
							{mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
						</button>
					</div>
				</div>

				{/* Mobile Menu */}
				{mobileMenuOpen && (
					<div className="md:hidden mt-4 pb-4 border-t border-border pt-4">
						<div className="flex flex-col space-y-1">
							{navLinks.map((link) => {
								const Icon = link.icon
								const articles = navPreviewData[link.key] || []
								const isExpanded = mobileExpandedItem === link.key
								return (
									<div key={link.href}>
										<button
											onClick={() => toggleMobileExpand(link.key)}
											className={`flex items-center justify-between w-full px-4 py-2.5 hover:bg-white/5 rounded-lg transition ${
												isExpanded ? 'text-[hsl(var(--nav-theme-light))]' : ''
											}`}
										>
											<span className="flex items-center gap-3">
												<Icon className="w-5 h-5" />
												{link.label}
											</span>
											<ChevronDown className={`w-4 h-4 transition-transform ${isExpanded ? 'rotate-180' : ''}`} />
										</button>
										{isExpanded && (
											<div className="ml-8 mr-4 mb-2 border-l-2 border-border pl-3">
												{mobileRandomArticles.map((article) => (
													<Link
														key={article.slug}
														href={`/${link.key}/${article.slug}`}
														className="flex items-center gap-2 py-2 text-sm text-foreground hover:text-[hsl(var(--nav-theme-light))] transition-colors"
														onClick={() => { setMobileMenuOpen(false); setMobileExpandedItem(null) }}
													>
														<ChevronRight className="w-3 h-3 text-[hsl(var(--nav-theme-light))] flex-shrink-0" />
														<span>{extractPrimaryKeyword(article.title)}</span>
													</Link>
												))}
												{mobileRandomArticles.length === 0 && (
													<div className="py-2 text-sm text-muted-foreground">
														No articles yet
													</div>
												)}
												{articles.length > 1 && (
													<Link
														href={link.href}
														className="flex items-center gap-1 py-2 text-sm font-medium text-[hsl(var(--nav-theme-light))]"
														onClick={() => { setMobileMenuOpen(false); setMobileExpandedItem(null) }}
													>
														{t('common.readMore')}
														<ChevronRight className="w-3.5 h-3.5" />
													</Link>
												)}
											</div>
										)}
									</div>
								)
							})}
							<div className="flex items-center gap-3 px-4 pt-2">
								<ThemeToggle />
							</div>
							{/* More Wikis - Mobile */}
							<div className="px-4">
								<button
									onClick={() => setMobileWikiExpanded(!mobileWikiExpanded)}
									className="flex items-center justify-between w-full py-2.5 hover:bg-white/5 rounded-lg transition"
								>
									<span className="flex items-center gap-3 font-medium">
										<ExternalLink className="w-5 h-5" />
										More Wikis
									</span>
									<ChevronDown className={`w-4 h-4 transition-transform ${mobileWikiExpanded ? 'rotate-180' : ''}`} />
								</button>
								{mobileWikiExpanded && (
									<div className="ml-8 mr-0 mb-2 border-l-2 border-border pl-3">
										{wikiLinks.map((wiki) => (
											<a
												key={wiki.url}
												href={wiki.url}
												target="_blank"
												rel="noopener noreferrer"
												className="flex items-center gap-2 py-2 text-sm text-foreground hover:text-[hsl(var(--nav-theme-light))] transition-colors"
												onClick={() => { setMobileMenuOpen(false); setMobileWikiExpanded(false) }}
											>
												<ChevronRight className="w-3 h-3 text-[hsl(var(--nav-theme-light))] flex-shrink-0" />
												<span className="line-clamp-1">{wiki.name}</span>
											</a>
										))}
									</div>
								)}
							</div>
						</div>
					</div>
				)}
			</div>
		</nav>
	)
}

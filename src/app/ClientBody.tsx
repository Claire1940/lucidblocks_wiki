'use client'

import { useEffect } from 'react'
import Navigation from '@/components/Navigation'
import { ThemeProvider } from '@/components/ThemeProvider'
import type { NavPreviewData } from '@/types/nav-preview'
import type { WikiLink } from '@/lib/wiki-links'

interface ClientBodyProps {
	children: React.ReactNode
	navPreviewData: NavPreviewData
	wikiLinks: WikiLink[]
}

export default function ClientBody({ children, navPreviewData, wikiLinks }: ClientBodyProps) {
	// Remove any extension-added classes during hydration
	useEffect(() => {
		// This runs only on the client after hydration
		document.body.className = 'antialiased'
	}, [])

	return (
		<ThemeProvider attribute="class" defaultTheme="dark" enableSystem={false}>
			<div className="antialiased">
				<Navigation navPreviewData={navPreviewData} wikiLinks={wikiLinks} />
				<main className="pt-20">{children}</main>
			</div>
		</ThemeProvider>
	)
}



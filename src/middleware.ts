import createMiddleware from 'next-intl/middleware'
import { routing } from './i18n/routing'

// alternateLinks: false 禁用 next-intl 自动生成的 Link 响应头（它从请求 proto 取值，
// 经 Traefik→容器内部链路时 proto 是 http，导致 hreflang 泄漏 http://）。
// hreflang 仍由 generateMetadata 的 HTML <link rel="alternate"> 输出（见 i18n-utils.ts），已强制 https。
export default createMiddleware({ ...routing, alternateLinks: false })

export const config = {
	matcher: [
		// 匹配所有路径，排除静态资源
		'/((?!api|_next/static|_next/image|favicon.ico|.*\\..*).*)',
		'/',
	],
}

import createMiddleware from 'next-intl/middleware'
import { routing } from './i18n/routing'

export default createMiddleware(routing)

export const config = {
	matcher: [
		// 匹配所有路径，排除静态资源
		'/((?!api|_next/static|_next/image|favicon.ico|.*\\..*).*)',
		'/',
	],
}

/**
 * 平滑滚动到指定的页面锚点
 * @param sectionId - 目标 section 的 ID
 */
export function scrollToSection(sectionId: string) {
  const element = document.getElementById(sectionId)
  if (!element) {
    console.warn(`Section "${sectionId}" not found`)
    return
  }

  // 检测用户运动偏好
  const prefersReducedMotion = window.matchMedia(
    '(prefers-reduced-motion: reduce)'
  ).matches

  element.scrollIntoView({
    behavior: prefersReducedMotion ? 'auto' : 'smooth',
    block: 'start',
    inline: 'nearest',
  })

  // 更新 URL hash（不触发跳转）
  window.history.replaceState(
    null,
    '',
    `${window.location.pathname}#${sectionId}`
  )
}

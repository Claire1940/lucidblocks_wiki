import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * 从文章标题中提取主关键词（冒号之前的部分）
 * 例如："Heartopia PC Download: Complete Guide 2026" -> "Heartopia PC Download"
 * 如果标题中没有冒号，返回完整标题
 */
export function extractPrimaryKeyword(title: string): string {
  // 优先按 ' - ' 截断（如 "Game Name - Details"）
  const dashIndex = title.indexOf(' - ')
  if (dashIndex !== -1) {
    return title.substring(0, dashIndex).trim()
  }
  // 有多个冒号时截取最后一个冒号前（如 "Game: Subtitle: Details"）
  const lastColonIndex = title.lastIndexOf(':')
  const firstColonIndex = title.indexOf(':')
  if (lastColonIndex !== -1 && lastColonIndex !== firstColonIndex) {
    return title.substring(0, lastColonIndex).trim()
  }
  // 只有一个冒号或无冒号，返回完整标题
  return title
}

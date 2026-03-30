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
  const colonIndex = title.indexOf(':')
  if (colonIndex === -1) {
    return title
  }
  return title.substring(0, colonIndex).trim()
}

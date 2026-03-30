import fs from 'fs'
import path from 'path'

export interface WikiLink {
  name: string
  url: string
}

const SITE_JSON_PATH = path.join(process.cwd(), 'site.json')

function toTitleCase(str: string): string {
  return str.replace(/\b\w/g, c => c.toUpperCase())
}

export function getWikiLinks(max = 10): WikiLink[] {
  try {
    const raw = JSON.parse(fs.readFileSync(SITE_JSON_PATH, 'utf-8'))
    const sites = raw.sites
      .filter((s: any) => s.status === '已上线')
      .sort((a: any, b: any) => new Date(b.launchDate).getTime() - new Date(a.launchDate).getTime())
      .slice(0, max)

    return sites.map((s: any) => ({
      name: toTitleCase(s.keywords),
      url: `https://www.${s.domain}`,
    }))
  } catch {
    return []
  }
}

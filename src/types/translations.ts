/**
 * Translation Types
 *
 * 这个文件定义了所有翻译数据的类型
 * 遵循三层架构：数据层（JSON）→ 适配层（验证）→ 组件层（使用）
 */

// ============================================
// 基础类型
// ============================================

export interface IconCard {
  icon: string
  title: string
  description: string
}

export interface Stat {
  value: string
  label: string
}

export interface Step {
  title: string
  description: string
}

export interface Section {
  title: string
  items: string[]
}

export interface Role {
  name: string
  description: string
  tips: string[]
}

export interface TaskType {
  type: string
  examples: string[]
}

export interface Keybind {
  action: string
  key: string
}

export interface Equipment {
  name: string
  description: string
}

export interface Category {
  name: string
  examples: string[]
}

// ============================================
// 模块类型（数据层 - 反映 JSON 结构）
// ============================================

export interface DemoDownloadModule {
  title: string
  subtitle: string
  sections?: Section[]  // 可选，因为 JSON 可能没有
}

export interface BeginnerGuideModule {
  title: string
  subtitle: string
  steps?: Step[]
  pitfalls?: Array<{
    title: string
    description: string
  }>
}

export interface CoopGuideModule {
  title: string
  subtitle: string
  roles?: Role[]
  threats?: string[]
}

export interface TasksObjectivesModule {
  title: string
  subtitle: string
  taskTypes?: TaskType[]
  efficiency?: string[]
}

export interface ControlsKeybindsModule {
  title: string
  subtitle: string
  keybinds?: Keybind[]
}

export interface ContentSettingsModule {
  title: string
  subtitle: string
  descriptors?: string[]
  details?: Section[]
}

export interface CraftingEquipmentModule {
  title: string
  subtitle: string
  equipment?: Equipment[]
  sections?: Section[]
}

export interface LootItemsModule {
  title: string
  subtitle: string
  categories?: Category[]
}

// ============================================
// 完整的翻译结构（数据层）
// ============================================

export interface Translations {
  seo: {
    home: {
      title: string
      description: string
      keywords: string
      ogTitle: string
      ogDescription: string
      twitterTitle: string
      twitterDescription: string
    }
  }
  nav: Record<string, string>
  common: {
    home: string
    more: string
    playNow: string
    switchLanguage: string
    switchTheme: string
    lightMode: string
    darkMode: string
    notFound: string
    notFoundDescription: string
    backToHome: string
    relatedArticles: string
    readMore: string
  }
  hero: {
    badge: string
    title: string
    description: string
    getFreeCodesCTA: string
    playOnRobloxCTA: string
    stats: Record<string, Stat>
  }
  gameFeature: {
    title: string
    description: string
  }
  tools: {
    title: string
    titleHighlight: string
    subtitle: string
    cards?: IconCard[]  // 可选
  }
  modules: {
    demoDownload?: DemoDownloadModule
    beginnerGuide?: BeginnerGuideModule
    coopGuide?: CoopGuideModule
    tasksObjectives?: TasksObjectivesModule
    controlsKeybinds?: ControlsKeybindsModule
    contentSettings?: ContentSettingsModule
    craftingEquipment?: CraftingEquipmentModule
    lootItems?: LootItemsModule
  }
}

// ============================================
// 组件 Props 类型（组件层 - 必需字段）
// ============================================

export interface IconCardListProps {
  cards: IconCard[]  // 必需！组件要求数据存在
  onCardClick?: (index: number) => void
}

export interface StepListProps {
  steps: Step[]  // 必需！
}

export interface SectionListProps {
  sections: Section[]  // 必需！
}

export interface RoleListProps {
  roles: Role[]  // 必需！
}

// ============================================
// 类型守卫（运行时验证）
// ============================================

export function isIconCard(obj: any): obj is IconCard {
  return (
    typeof obj === 'object' &&
    typeof obj.icon === 'string' &&
    typeof obj.title === 'string' &&
    typeof obj.description === 'string'
  )
}

export function isValidArray<T>(
  arr: any,
  validator: (item: any) => item is T
): arr is T[] {
  return Array.isArray(arr) && arr.every(validator)
}

// ============================================
// 辅助函数（适配层）
// ============================================

/**
 * 安全地获取数组，如果不存在或无效则返回空数组
 */
export function safeArray<T>(
  arr: T[] | undefined | null,
  validator?: (item: any) => item is T
): T[] {
  if (!arr || !Array.isArray(arr)) {
    return []
  }

  if (validator) {
    return arr.filter(validator)
  }

  return arr
}

/**
 * 安全地获取对象，如果不存在则返回默认值
 */
export function safeObject<T extends object>(
  obj: T | undefined | null,
  defaultValue: T
): T {
  return obj || defaultValue
}

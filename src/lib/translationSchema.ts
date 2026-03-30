/**
 * Translation Schema Validation
 *
 * 使用 Zod 在运行时验证翻译数据的完整性
 * 在开发环境中，如果数据不符合预期，会提供详细的错误信息
 */

import { z } from 'zod'

// ============================================
// 基础 Schema
// ============================================

export const IconCardSchema = z.object({
  icon: z.string().min(1, 'Icon name is required'),
  title: z.string().min(1, 'Title is required'),
  description: z.string().min(1, 'Description is required')
})

export const StatSchema = z.object({
  value: z.string(),
  label: z.string()
})

export const StepSchema = z.object({
  title: z.string(),
  description: z.string()
})

export const SectionSchema = z.object({
  title: z.string(),
  items: z.array(z.string())
})

export const RoleSchema = z.object({
  name: z.string(),
  description: z.string(),
  tips: z.array(z.string())
})

export const TaskTypeSchema = z.object({
  type: z.string(),
  examples: z.array(z.string())
})

export const KeybindSchema = z.object({
  action: z.string(),
  key: z.string()
})

export const EquipmentSchema = z.object({
  name: z.string(),
  description: z.string()
})

export const CategorySchema = z.object({
  name: z.string(),
  examples: z.array(z.string())
})

// ============================================
// 模块 Schema
// ============================================

export const DemoDownloadModuleSchema = z.object({
  title: z.string(),
  subtitle: z.string(),
  sections: z.array(SectionSchema).optional()
})

export const BeginnerGuideModuleSchema = z.object({
  title: z.string(),
  subtitle: z.string(),
  steps: z.array(StepSchema).optional(),
  pitfalls: z.array(z.object({
    title: z.string(),
    description: z.string()
  })).optional()
})

export const CoopGuideModuleSchema = z.object({
  title: z.string(),
  subtitle: z.string(),
  roles: z.array(RoleSchema).optional(),
  threats: z.array(z.string()).optional()
})

export const TasksObjectivesModuleSchema = z.object({
  title: z.string(),
  subtitle: z.string(),
  taskTypes: z.array(TaskTypeSchema).optional(),
  efficiency: z.array(z.string()).optional()
})

export const ControlsKeybindsModuleSchema = z.object({
  title: z.string(),
  subtitle: z.string(),
  keybinds: z.array(KeybindSchema).optional()
})

export const ContentSettingsModuleSchema = z.object({
  title: z.string(),
  subtitle: z.string(),
  descriptors: z.array(z.string()).optional(),
  details: z.array(SectionSchema).optional()
})

export const CraftingEquipmentModuleSchema = z.object({
  title: z.string(),
  subtitle: z.string(),
  equipment: z.array(EquipmentSchema).optional(),
  sections: z.array(SectionSchema).optional()
})

export const LootItemsModuleSchema = z.object({
  title: z.string(),
  subtitle: z.string(),
  categories: z.array(CategorySchema).optional()
})

// ============================================
// 完整的翻译 Schema
// ============================================

export const TranslationsSchema = z.object({
  seo: z.object({
    home: z.object({
      title: z.string(),
      description: z.string(),
      keywords: z.string(),
      ogTitle: z.string(),
      ogDescription: z.string(),
      twitterTitle: z.string(),
      twitterDescription: z.string()
    })
  }),
  nav: z.record(z.string(), z.string()),
  common: z.object({
    home: z.string(),
    more: z.string(),
    playNow: z.string(),
    switchLanguage: z.string(),
    switchTheme: z.string(),
    lightMode: z.string(),
    darkMode: z.string(),
    notFound: z.string(),
    notFoundDescription: z.string(),
    backToHome: z.string(),
    relatedArticles: z.string(),
    readMore: z.string()
  }),
  hero: z.object({
    badge: z.string(),
    title: z.string(),
    description: z.string(),
    getFreeCodesCTA: z.string(),
    playOnRobloxCTA: z.string(),
    stats: z.record(z.string(), StatSchema)
  }),
  gameFeature: z.object({
    title: z.string(),
    description: z.string()
  }),
  tools: z.object({
    title: z.string(),
    titleHighlight: z.string(),
    subtitle: z.string(),
    cards: z.array(IconCardSchema).optional()
  }),
  modules: z.object({
    demoDownload: DemoDownloadModuleSchema.optional(),
    beginnerGuide: BeginnerGuideModuleSchema.optional(),
    coopGuide: CoopGuideModuleSchema.optional(),
    tasksObjectives: TasksObjectivesModuleSchema.optional(),
    controlsKeybinds: ControlsKeybindsModuleSchema.optional(),
    contentSettings: ContentSettingsModuleSchema.optional(),
    craftingEquipment: CraftingEquipmentModuleSchema.optional(),
    lootItems: LootItemsModuleSchema.optional()
  })
})

// ============================================
// 验证函数
// ============================================

/**
 * 验证翻译数据
 * 在开发环境中会打印详细的错误信息
 */
export function validateTranslations(data: unknown, locale: string) {
  const result = TranslationsSchema.safeParse(data)

  if (!result.success) {
    if (process.env.NODE_ENV === 'development') {
      console.error(`❌ Translation validation failed for locale: ${locale}`)
      console.error('Errors:', result.error.format())

      // 打印每个错误的详细路径
      result.error.issues.forEach(issue => {
        console.error(`  - ${issue.path.join('.')}: ${issue.message}`)
      })
    }

    return {
      success: false,
      error: result.error
    }
  }

  if (process.env.NODE_ENV === 'development') {
    console.log(`✅ Translation validation passed for locale: ${locale}`)
  }

  return {
    success: true,
    data: result.data
  }
}

/**
 * 验证特定模块的数据
 */
export function validateModule<T>(
  data: unknown,
  schema: z.ZodSchema<T>,
  moduleName: string
): { success: boolean; data?: T; error?: z.ZodError } {
  const result = schema.safeParse(data)

  if (!result.success) {
    if (process.env.NODE_ENV === 'development') {
      console.error(`❌ Module validation failed: ${moduleName}`)
      console.error('Errors:', result.error.format())
    }

    return {
      success: false,
      error: result.error
    }
  }

  return {
    success: true,
    data: result.data
  }
}

// ============================================
// 类型推导（从 Schema 自动生成 TypeScript 类型）
// ============================================

export type Translations = z.infer<typeof TranslationsSchema>
export type IconCard = z.infer<typeof IconCardSchema>
export type Stat = z.infer<typeof StatSchema>
export type Step = z.infer<typeof StepSchema>
export type Section = z.infer<typeof SectionSchema>
export type Role = z.infer<typeof RoleSchema>
export type TaskType = z.infer<typeof TaskTypeSchema>
export type Keybind = z.infer<typeof KeybindSchema>
export type Equipment = z.infer<typeof EquipmentSchema>
export type Category = z.infer<typeof CategorySchema>

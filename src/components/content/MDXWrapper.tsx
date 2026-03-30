export async function MDXWrapper({
  language,
  slug,
  contentType = 'guide'
}: {
  language: string
  slug: string
  contentType?: string
}) {
  try {
    // 动态导入 MDX 文件
    const MDXContent = await import(`@/../../content/${language}/${contentType}/${slug}.mdx`)

    return <MDXContent.default />
  } catch (error) {
    console.error(`Failed to load MDX: ${language}/${contentType}/${slug}`, error)
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Content not found</p>
      </div>
    )
  }
}

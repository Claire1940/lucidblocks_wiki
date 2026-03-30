'use client'

interface StatItem {
  value: string
  label: string
}

interface HeroStatsProps {
  stats: StatItem[]
}

export default function HeroStats({ stats }: HeroStatsProps) {
  return (
    <div className="scroll-reveal grid grid-cols-2 md:grid-cols-4 gap-6 max-w-4xl mx-auto">
      {stats.map((stat, index) => (
        <div key={index} className="p-6 bg-white/5 border border-border rounded-lg">
          <div className="text-3xl md:text-4xl font-bold text-[hsl(var(--nav-theme-light))] mb-2">
            {stat.value}
          </div>
          <div className="text-sm text-muted-foreground">{stat.label}</div>
        </div>
      ))}
    </div>
  )
}
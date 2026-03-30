'use client'

interface RarityTier {
  name: string
  rate: string
  description: string
}

interface RarityTiersProps {
  title: string
  titleHighlight: string
  subtitle: string
  tiers: {
    common: RarityTier
    rare: RarityTier
    epic: RarityTier
    legendary: RarityTier
    mythic: RarityTier
    secret: RarityTier
  }
}

export default function RarityTiers({ title, titleHighlight, subtitle, tiers }: RarityTiersProps) {
  const rarityData = [
    { ...tiers.common, color: 'bg-gray-500' },
    { ...tiers.rare, color: 'bg-blue-500' },
    { ...tiers.epic, color: 'bg-purple-500' },
    { ...tiers.legendary, color: 'bg-orange-500' },
    { ...tiers.mythic, color: 'bg-red-500' },
    { ...tiers.secret, color: 'bg-green-500' }
  ]

  return (
    <section className="px-4 py-20">
      <div className="container mx-auto">
        <div className="text-center mb-12">
          <h2 className="scroll-reveal text-4xl md:text-5xl font-bold mb-4">
            {title} <span className="text-[hsl(var(--nav-theme-light))]">{titleHighlight}</span>
          </h2>
          <p className="scroll-reveal text-muted-foreground text-lg">
            {subtitle}
          </p>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 max-w-6xl mx-auto">
          {rarityData.map((rarity, index) => (
            <div key={index} className="scroll-reveal p-6 bg-white/5 border border-border rounded-xl text-center">
              <div className={`w-16 h-16 ${rarity.color} rounded-lg mx-auto mb-4`}></div>
              <h3 className="font-bold mb-2">{rarity.name}</h3>
              <div className="text-[hsl(var(--nav-theme-light))] text-sm font-semibold mb-2">{rarity.rate}</div>
              <p className="text-xs text-muted-foreground">{rarity.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
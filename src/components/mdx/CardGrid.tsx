interface CardGridProps {
  cols?: 2 | 3 | 4
  children: React.ReactNode
}

export function CardGrid({ cols = 2, children }: CardGridProps) {
  const gridCols = {
    2: 'md:grid-cols-2',
    3: 'md:grid-cols-3',
    4: 'md:grid-cols-4',
  }

  return (
    <div className={`grid ${gridCols[cols]} gap-6`}>
      {children}
    </div>
  )
}

interface CardProps {
  title: string
  children: React.ReactNode
}

export function Card({ title, children }: CardProps) {
  return (
    <div className="bg-card border border-border rounded-xl p-6 hover:border-blue-500 transition-colors">
      <h3 className="text-xl font-bold text-foreground mb-3">{title}</h3>
      <div className="text-muted-foreground">{children}</div>
    </div>
  )
}

interface StepsProps {
  children: React.ReactNode
}

export function Steps({ children }: StepsProps) {
  return (
    <div className="space-y-3">
      {children}
    </div>
  )
}

interface StepProps {
  num: string | number
  title: string
  children: React.ReactNode
}

export function Step({ num, title, children }: StepProps) {
  return (
    <div className="flex gap-4 items-center">
      <div className="flex-shrink-0 w-10 h-10 rounded-full bg-blue-500 text-white flex items-center justify-center font-bold text-base">
        {num}
      </div>
      <div className="flex-1">
        <h4 className="text-xl font-bold text-foreground mb-2">{title}</h4>
        <div className="text-muted-foreground">{children}</div>
      </div>
    </div>
  )
}

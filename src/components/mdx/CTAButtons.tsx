import { Link } from '@/i18n/navigation'

interface Button {
  label: string
  href: string
  variant?: 'primary' | 'secondary'
}

interface CTAButtonsProps {
  buttons: Button[]
}

export function CTAButtons({ buttons }: CTAButtonsProps) {
  return (
    <div className="flex justify-center gap-4 flex-wrap py-12">
      {buttons.map((button, index) => (
        <Link
          key={index}
          href={button.href}
          className={`px-6 py-3 rounded-xl font-bold transition ${
            button.variant === 'primary'
              ? 'bg-blue-500 hover:bg-blue-600 text-white'
              : 'bg-secondary hover:bg-secondary/80 text-foreground'
          }`}
        >
          {button.label}
        </Link>
      ))}
    </div>
  )
}

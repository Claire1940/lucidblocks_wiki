'use client'

interface LoadingPlaceholderProps {
  height?: string
  className?: string
}

export default function LoadingPlaceholder({
  height = "h-32",
  className = ""
}: LoadingPlaceholderProps) {
  return (
    <div className={`${height} ${className} flex items-center justify-center`}>
      <div className="animate-pulse flex space-x-4 w-full max-w-4xl mx-auto px-4">
        <div className="flex-1 space-y-6 py-1">
          <div className="h-4 bg-white/10 rounded w-3/4 mx-auto"></div>
          <div className="space-y-3">
            <div className="grid grid-cols-3 gap-4">
              <div className="h-8 bg-white/10 rounded col-span-2"></div>
              <div className="h-8 bg-white/10 rounded col-span-1"></div>
            </div>
            <div className="h-4 bg-white/10 rounded w-5/6"></div>
            <div className="h-4 bg-white/10 rounded w-4/6"></div>
          </div>
        </div>
      </div>
    </div>
  )
}
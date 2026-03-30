'use client'

import { useState } from 'react'
import Image from 'next/image'
import { Play } from 'lucide-react'

interface VideoFeatureProps {
  videoId: string
  title: string
  posterImage: string
}

export function VideoFeature({ videoId, title, posterImage }: VideoFeatureProps) {
  const [isPlaying, setIsPlaying] = useState(false)

  const handlePlay = () => {
    setIsPlaying(true)
  }

  return (
    <div className="relative w-full" style={{ paddingBottom: '56.25%' }}>
      {!isPlaying ? (
        <>
          {/* 占位图片 */}
          <Image
            src={posterImage}
            alt={title}
            fill
            className="object-cover rounded-lg"
            priority
          />
          {/* 播放按钮覆盖层 */}
          <div
            className="absolute inset-0 flex items-center justify-center bg-black/30 hover:bg-black/40 transition-colors cursor-pointer rounded-lg"
            onClick={handlePlay}
          >
            <div className="w-20 h-20 bg-red-600 hover:bg-red-700 rounded-full flex items-center justify-center transition-colors">
              <Play className="w-10 h-10 text-white ml-1" fill="white" />
            </div>
          </div>
        </>
      ) : (
        /* YouTube iframe */
        <iframe
          className="absolute top-0 left-0 w-full h-full rounded-lg"
          src={`https://www.youtube.com/embed/${videoId}?autoplay=1`}
          title={title}
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
        />
      )}
    </div>
  )
}

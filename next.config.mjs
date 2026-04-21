import createMDX from '@next/mdx'
import createNextIntlPlugin from 'next-intl/plugin'
import remarkGfm from 'remark-gfm'

const withNextIntl = createNextIntlPlugin('./src/i18n/request.ts')

/** @type {import('next').NextConfig} */
const nextConfig = {
  pageExtensions: ['js', 'jsx', 'md', 'mdx', 'ts', 'tsx'],
  allowedDevOrigins: ["*.preview.same-app.com"],

  // Docker 部署配置
  output: 'standalone',

  // URL 不加尾部斜杠
  trailingSlash: false,

  // 性能优化
  compress: true,
  poweredByHeader: false,

  // 实验性功能
  experimental: {
    optimizePackageImports: ['@/components/ui'],
  },

  images: {
    unoptimized: false,
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
    domains: [
      "source.unsplash.com",
      "images.unsplash.com",
      "ext.same-assets.com",
      "ugc.same-assets.com",
    ],
    remotePatterns: [
      {
        protocol: "https",
        hostname: "source.unsplash.com",
        pathname: "/**",
      },
      {
        protocol: "https",
        hostname: "images.unsplash.com",
        pathname: "/**",
      },
      {
        protocol: "https",
        hostname: "ext.same-assets.com",
        pathname: "/**",
      },
      {
        protocol: "https",
        hostname: "ugc.same-assets.com",
        pathname: "/**",
      },
    ],
  },
};

const withMDX = createMDX({
  // 添加 markdown 插件
  options: {
    remarkPlugins: [remarkGfm],
    rehypePlugins: [],
  },
})

export default withNextIntl(withMDX(nextConfig))

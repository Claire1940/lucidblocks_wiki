import Link from 'next/link'
import type { Metadata } from 'next'
import { buildLanguageAlternates } from '@/lib/i18n-utils'
import { type Locale } from '@/i18n/routing'

interface Props {
  params: Promise<{ locale: string }>
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { locale } = await params
  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || 'https://www.lucidblocks.wiki'
  const path = '/privacy-policy'

  return {
    title: 'Privacy Policy - Lucid Blocks Wiki',
    description: 'Lucid Blocks Wiki Privacy Policy. Learn how we collect, use, and protect your data when you use our Steam game resource platform. Your privacy matters to us.',
    robots: {
      index: false,
      follow: true,
      googleBot: {
        index: false,
        follow: true,
        'max-video-preview': -1,
        'max-image-preview': 'large',
        'max-snippet': -1,
      },
    },
    openGraph: {
      type: 'website',
      locale: locale,
      url: locale === 'en' ? `${siteUrl}${path}` : `${siteUrl}/${locale}${path}`,
      siteName: 'Lucid Blocks Wiki',
      title: 'Privacy Policy - Lucid Blocks Wiki',
      description: 'Learn how we protect your privacy and handle your data.',
      images: [
        {
          url: `${siteUrl}/og-image.jpg`,
          width: 1200,
          height: 630,
          alt: 'Lucid Blocks Wiki',
        },
      ],
    },
    twitter: {
      card: 'summary_large_image',
      title: 'Privacy Policy - Lucid Blocks Wiki',
      description: 'Learn how we protect your privacy and handle your data.',
      images: [`${siteUrl}/og-image.jpg`],
    },
    alternates: buildLanguageAlternates(path, locale as Locale, siteUrl),
  }
}

export default function PrivacyPolicy() {
  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <section className="relative py-20 px-4 border-b border-border">
        <div className="container mx-auto max-w-4xl text-center">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Privacy Policy
          </h1>
          <p className="text-slate-300 text-lg mb-2">
            How we collect, use, and protect your information
          </p>
          <p className="text-slate-400 text-sm">
            Last Updated: March 14, 2026
          </p>
        </div>
      </section>

      {/* Content Section */}
      <section className="py-12 px-4">
        <div className="container mx-auto max-w-4xl">
          <div className="prose prose-invert prose-slate max-w-none">
            <h2>1. Information Collection</h2>
            <p>
              Lucid Blocks Wiki ("we", "our", or "us") collects minimal information to provide and improve our services.
              We collect information in the following ways:
            </p>
            <ul>
              <li><strong>Automatically Collected Data:</strong> When you visit our website, we automatically collect certain information about your device, including your IP address, browser type, operating system, and browsing behavior through analytics tools.</li>
              <li><strong>Language Preferences:</strong> We store your language preference in your browser's local storage to enhance your experience.</li>
              <li><strong>Cookies:</strong> We use cookies and similar tracking technologies to track activity on our website and store certain information.</li>
            </ul>

            <h2>2. Use of Data</h2>
            <p>We use the collected information for the following purposes:</p>
            <ul>
              <li>To provide, maintain, and improve our website and services</li>
              <li>To understand how users interact with our content</li>
              <li>To analyze website traffic and user behavior</li>
              <li>To detect, prevent, and address technical issues</li>
              <li>To optimize website performance and user experience</li>
            </ul>

            <h2>3. Cookies and Analytics</h2>
            <h3>Google Analytics</h3>
            <p>
              We use Google Analytics (GA4) to collect and analyze information about how visitors use our website.
              Google Analytics collects anonymous information such as:
            </p>
            <ul>
              <li>Pages viewed and time spent on each page</li>
              <li>Browser type and device information</li>
              <li>Geographic location (country/city level)</li>
              <li>Referral sources (how you found our website)</li>
            </ul>
            <p>
              This data is used solely to improve our website experience. You can opt-out of Google Analytics by
              installing the <a href="https://tools.google.com/dlpage/gaoptout" target="_blank" rel="noopener noreferrer" className="text-[hsl(var(--nav-theme-light))] hover:underline">Google Analytics Opt-out Browser Add-on</a>.
            </p>

            <h3>Microsoft Clarity</h3>
            <p>
              We use Microsoft Clarity to understand how users interact with our website through session recordings
              and heatmaps. Clarity collects:
            </p>
            <ul>
              <li>Mouse movements, clicks, and scroll behavior</li>
              <li>Page navigation patterns</li>
              <li>Device and browser information</li>
            </ul>
            <p>
              All data collected is anonymized and does not include personally identifiable information.
              Learn more about <a href="https://privacy.microsoft.com/en-us/privacystatement" target="_blank" rel="noopener noreferrer" className="text-[hsl(var(--nav-theme-light))] hover:underline">Microsoft's privacy practices</a>.
            </p>

            <h3>Managing Cookies</h3>
            <p>
              You can control and manage cookies through your browser settings. Please note that disabling cookies
              may affect your experience on our website. Most browsers allow you to:
            </p>
            <ul>
              <li>View what cookies are stored and delete them individually</li>
              <li>Block third-party cookies</li>
              <li>Block all cookies</li>
              <li>Delete all cookies when you close your browser</li>
            </ul>

            <h2>4. Third-Party Services</h2>
            <p>
              Our website may contain links to external websites, including Steam, Discord, and social media platforms.
              We are not responsible for the privacy practices or content of these third-party sites. We encourage
              you to review their privacy policies before providing any personal information.
            </p>
            <p>
              Third-party services we use include:
            </p>
            <ul>
              <li><strong>Google Analytics:</strong> Web analytics service</li>
              <li><strong>Microsoft Clarity:</strong> Behavioral analytics service</li>
              <li><strong>Netlify:</strong> Hosting and CDN provider</li>
            </ul>

            <h2>5. Children's Privacy</h2>
            <p>
              Our website is intended for a general audience and does not knowingly collect personal information
              from children under the age of 13. If you are a parent or guardian and believe your child has
              provided us with personal information, please contact us immediately, and we will take steps to
              remove such information.
            </p>
            <p>
              We comply with the Children's Online Privacy Protection Act (COPPA) and do not knowingly collect,
              use, or disclose personal information from children.
            </p>

            <h2>6. Data Security</h2>
            <p>
              We implement reasonable security measures to protect the information collected through our website.
              However, please be aware that no method of transmission over the internet or electronic storage is
              100% secure. While we strive to protect your information, we cannot guarantee absolute security.
            </p>

            <h2>7. Data Retention</h2>
            <p>
              We retain analytics data for as long as necessary to fulfill the purposes outlined in this Privacy Policy,
              unless a longer retention period is required by law. Analytics data is typically retained for 26 months
              in Google Analytics.
            </p>

            <h2>8. Your Rights</h2>
            <p>
              Depending on your location, you may have the following rights regarding your information:
            </p>
            <ul>
              <li>The right to access the information we have about you</li>
              <li>The right to request correction of inaccurate data</li>
              <li>The right to request deletion of your data</li>
              <li>The right to opt-out of analytics tracking</li>
              <li>The right to withdraw consent at any time</li>
            </ul>

            <h2>9. International Users</h2>
            <p>
              Our website is hosted in the United States. If you are accessing our website from outside the United States,
              please be aware that your information may be transferred to, stored, and processed in the United States or
              other countries where our service providers operate.
            </p>

            <h2>10. Changes to Privacy Policy</h2>
            <p>
              We reserve the right to update or modify this Privacy Policy at any time. When we make changes, we will
              update the "Last Updated" date at the top of this page. We encourage you to review this Privacy Policy
              periodically to stay informed about how we protect your information.
            </p>
            <p>
              Significant changes to this Privacy Policy will be communicated through a notice on our homepage or
              via other appropriate channels.
            </p>

            <h2>11. Disclaimer</h2>
            <p>
              Lucid Blocks Wiki is an unofficial fan-made website and is not affiliated with, endorsed by, or associated
              with Valve Corporation (Steam) or the developers of Lucid Blocks. All game content, trademarks, and assets are
              the property of their respective owners.
            </p>

            <h2>12. Contact Information</h2>
            <p>
              If you have any questions, concerns, or requests regarding this Privacy Policy or our data practices,
              please contact us at:
            </p>
            <p>
              <strong>Email:</strong> <a href="mailto:privacy@lucidblocks.wiki" className="text-[hsl(var(--nav-theme-light))] hover:underline">privacy@lucidblocks.wiki</a>
            </p>
            <p>
              We will respond to all legitimate requests within 30 days.
            </p>
          </div>
        </div>
      </section>

      {/* Back to Home */}
      <section className="py-8 px-4 border-t border-border">
        <div className="container mx-auto max-w-4xl text-center">
          <Link href="/" className="text-[hsl(var(--nav-theme-light))] hover:underline">
            ← Back to Home
          </Link>
        </div>
      </section>
    </div>
  )
}

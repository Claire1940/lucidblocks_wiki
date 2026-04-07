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
  const path = '/terms-of-service'

  return {
    title: "Terms of Service - Lucid Blocks Wiki",
    description: "Read the Terms of Service for Lucid Blocks Wiki. Learn about user responsibilities, content usage guidelines, and legal terms for using our Steam game resource platform.",
    keywords: [
      'terms of service',
      "Lucid Blocks Wiki terms",
      'user agreement',
      'legal terms',
      'usage policy',
    ],
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
      siteName: "Lucid Blocks Wiki",
      title: "Terms of Service - Lucid Blocks Wiki",
      description: "Terms and conditions for using Lucid Blocks Wiki.",
      images: [
        {
          url: `${siteUrl}/og-image.jpg`,
          width: 1200,
          height: 630,
          alt: "Lucid Blocks Wiki",
        },
      ],
    },
    twitter: {
      card: 'summary_large_image',
      title: "Terms of Service - Lucid Blocks Wiki",
      description: "Terms and conditions for using Lucid Blocks Wiki.",
      images: [`${siteUrl}/og-image.jpg`],
    },
    alternates: buildLanguageAlternates(path, locale as Locale, siteUrl),
  }
}

export default function TermsOfService() {
  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <section className="relative py-20 px-4 border-b border-border">
        <div className="container mx-auto max-w-4xl text-center">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Terms of Service
          </h1>
          <p className="text-slate-300 text-lg mb-2">
            Terms and conditions for using Lucid Blocks Wiki
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
            <h2>1. Acceptance of Terms</h2>
            <p>
              By accessing and using Lucid Blocks Wiki ("the Website", "we", "our", or "us"), you agree to be bound
              by these Terms of Service ("Terms"). If you do not agree to these Terms, please do not use our Website.
            </p>
            <p>
              These Terms constitute a legally binding agreement between you ("User", "you", or "your") and Lucid Blocks Wiki.
              Your continued use of the Website signifies your acceptance of these Terms and any future modifications.
            </p>

            <h2>2. Description of Service</h2>
            <p>
              Lucid Blocks Wiki is an unofficial, community-driven fan website that provides information, guides, tools,
              and resources related to the Steam game "Lucid Blocks". Our services include, but are not limited to:
            </p>
            <ul>
              <li>Game guides and survival strategies</li>
              <li>Crafting and Apotheosis fusion guides</li>
              <li>Biome and world region information</li>
              <li>Creature and enemy guides</li>
              <li>Achievement walkthroughs</li>
              <li>Community discussion and content</li>
            </ul>
            <p>
              <strong>Important:</strong> Lucid Blocks Wiki is NOT affiliated with, endorsed by, or associated with
              Valve Corporation (Steam) or the official developers of Lucid Blocks. We are an independent fan community.
            </p>

            <h2>3. User Responsibilities</h2>
            <h3>3.1 Acceptable Use</h3>
            <p>You agree to use the Website only for lawful purposes and in accordance with these Terms. You agree NOT to:</p>
            <ul>
              <li>Use the Website in any way that violates any applicable federal, state, local, or international law</li>
              <li>Engage in any conduct that restricts or inhibits anyone's use or enjoyment of the Website</li>
              <li>Transmit any viruses, malware, or other malicious code</li>
              <li>Attempt to gain unauthorized access to any portion of the Website or any systems or networks</li>
              <li>Use automated scripts, bots, or scrapers to collect data from the Website</li>
              <li>Reproduce, duplicate, copy, or resell any content from the Website for commercial purposes</li>
              <li>Impersonate any person or entity, or falsely state or misrepresent your affiliation with a person or entity</li>
            </ul>

            <h3>3.2 Account Conduct</h3>
            <p>
              While we do not currently require user accounts, if we implement such features in the future, you agree to:
            </p>
            <ul>
              <li>Provide accurate and complete information</li>
              <li>Maintain the security of your account credentials</li>
              <li>Be responsible for all activities under your account</li>
              <li>Notify us immediately of any unauthorized use</li>
            </ul>

            <h2>4. Intellectual Property</h2>
            <h3>4.1 Website Content</h3>
            <p>
              The Website and its original content, features, and functionality (including but not limited to text,
              graphics, logos, images, and software) are owned by Lucid Blocks Wiki and are protected by international
              copyright, trademark, and other intellectual property laws.
            </p>

            <h3>4.2 Game Content</h3>
            <p>
              All game-related content, including but not limited to character images, game screenshots, logos, and
              trademarks, are the property of Valve Corporation (Steam) and/or the developers of Lucid Blocks. We use such
              content under fair use principles for informational and educational purposes only.
            </p>

            <h3>4.3 User-Generated Content</h3>
            <p>
              If you submit content to our Website (such as comments, suggestions, or contributions), you grant us
              a worldwide, non-exclusive, royalty-free license to use, reproduce, modify, and display such content
              in connection with the Website.
            </p>

            <h2>5. Disclaimer of Warranties</h2>
            <p>
              THE WEBSITE IS PROVIDED ON AN "AS IS" AND "AS AVAILABLE" BASIS WITHOUT WARRANTIES OF ANY KIND, EITHER
              EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO:
            </p>
            <ul>
              <li><strong>Accuracy:</strong> We strive to provide accurate information, but we do not guarantee that all content is current, complete, or error-free. Game updates may render information outdated.</li>
              <li><strong>Availability:</strong> We do not guarantee that the Website will be available at all times or free from interruptions, errors, or technical issues.</li>
              <li><strong>Third-Party Content:</strong> We are not responsible for the accuracy or reliability of information obtained from third-party sources.</li>
              <li><strong>Demo Availability:</strong> Steam demo availability and game updates may change without notice. We are not responsible for demo access or game changes.</li>
            </ul>
            <p>
              You acknowledge that your use of the Website is at your sole risk and discretion.
            </p>

            <h2>6. Limitation of Liability</h2>
            <p>
              TO THE FULLEST EXTENT PERMITTED BY LAW, LUCID BLOCKS WIKI SHALL NOT BE LIABLE FOR ANY INDIRECT, INCIDENTAL,
              SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, OR ANY LOSS OF PROFITS OR REVENUES, WHETHER INCURRED DIRECTLY
              OR INDIRECTLY, OR ANY LOSS OF DATA, USE, GOODWILL, OR OTHER INTANGIBLE LOSSES, RESULTING FROM:
            </p>
            <ul>
              <li>Your use of or inability to use the Website</li>
              <li>Any conduct or content of any third party on the Website</li>
              <li>Any content obtained from the Website</li>
              <li>Unauthorized access, use, or alteration of your transmissions or content</li>
              <li>Reliance on information provided by the Website</li>
            </ul>
            <p>
              In no event shall our total liability to you for all damages exceed the amount of $100 USD or the amount
              you paid us in the last six months, whichever is less.
            </p>

            <h2>7. External Links</h2>
            <p>
              The Website may contain links to third-party websites, including Steam, Discord, social media platforms,
              and other external resources. These links are provided for your convenience only.
            </p>
            <p>
              We have no control over and assume no responsibility for the content, privacy policies, or practices
              of any third-party websites. You acknowledge and agree that we shall not be liable for any damage or
              loss caused by your use of any third-party websites.
            </p>

            <h2>8. Modifications to Terms</h2>
            <p>
              We reserve the right to modify or replace these Terms at any time at our sole discretion. We will provide
              notice of any material changes by:
            </p>
            <ul>
              <li>Updating the "Last Updated" date at the top of this page</li>
              <li>Posting a notice on our homepage</li>
              <li>Sending a notification through other appropriate channels (if applicable)</li>
            </ul>
            <p>
              Your continued use of the Website after any changes to these Terms constitutes acceptance of those changes.
              We encourage you to review these Terms periodically.
            </p>

            <h2>9. Modifications to Service</h2>
            <p>
              We reserve the right to modify, suspend, or discontinue any aspect of the Website at any time, with or
              without notice, for any reason. We shall not be liable to you or any third party for any modification,
              suspension, or discontinuance of the Website.
            </p>

            <h2>10. Termination</h2>
            <p>
              We may terminate or suspend your access to the Website immediately, without prior notice or liability,
              for any reason, including but not limited to:
            </p>
            <ul>
              <li>Violation of these Terms</li>
              <li>Fraudulent, abusive, or illegal activity</li>
              <li>Requests by law enforcement or government agencies</li>
            </ul>
            <p>
              Upon termination, your right to use the Website will immediately cease. All provisions of these Terms
              that by their nature should survive termination shall survive, including ownership provisions, warranty
              disclaimers, and limitations of liability.
            </p>

            <h2>11. Governing Law</h2>
            <p>
              These Terms shall be governed by and construed in accordance with the laws of the United States, without
              regard to its conflict of law provisions.
            </p>
            <p>
              Any disputes arising from or relating to these Terms or the Website shall be resolved through binding
              arbitration in accordance with the rules of the American Arbitration Association, except that either
              party may seek injunctive or other equitable relief in a court of competent jurisdiction.
            </p>

            <h2>12. Severability</h2>
            <p>
              If any provision of these Terms is held to be invalid or unenforceable by a court, the remaining provisions
              will remain in full force and effect. The invalid or unenforceable provision will be replaced with a valid
              provision that most closely matches the intent of the original provision.
            </p>

            <h2>13. Entire Agreement</h2>
            <p>
              These Terms, together with our Privacy Policy and Copyright Notice, constitute the entire agreement between
              you and Lucid Blocks Wiki regarding the use of the Website and supersede any prior agreements or understandings.
            </p>

            <h2>14. Contact Information</h2>
            <p>
              If you have any questions, concerns, or feedback regarding these Terms of Service, please contact us at:
            </p>
            <p>
              <strong>Email:</strong> <a href="mailto:legal@lucidblocks.wiki" className="text-[hsl(var(--nav-theme-light))] hover:underline">legal@lucidblocks.wiki</a>
            </p>
            <p>
              We will respond to all inquiries within a reasonable timeframe.
            </p>

            <h2>15. Acknowledgment</h2>
            <p>
              BY USING THE WEBSITE, YOU ACKNOWLEDGE THAT YOU HAVE READ THESE TERMS OF SERVICE AND AGREE TO BE BOUND BY THEM.
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

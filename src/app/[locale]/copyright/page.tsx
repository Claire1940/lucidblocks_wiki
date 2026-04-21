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
  const path = '/copyright'

  return {
    title: 'Copyright Notice - Lucid Blocks Wiki',
    description: 'Copyright and intellectual property information for Lucid Blocks Wiki. Learn about content ownership, fair use, DMCA policy, and how to report copyright infringement.',
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
      title: 'Copyright Notice - Lucid Blocks Wiki',
      description: 'Copyright and intellectual property information for Lucid Blocks Wiki.',
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
      title: 'Copyright Notice - Lucid Blocks Wiki',
      description: 'Copyright and intellectual property information.',
      images: [`${siteUrl}/og-image.jpg`],
    },
    alternates: buildLanguageAlternates(path, locale as Locale, siteUrl),
  }
}

export default function Copyright() {
  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <section className="relative py-20 px-4 border-b border-border">
        <div className="container mx-auto max-w-4xl text-center">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Copyright Notice
          </h1>
          <p className="text-slate-300 text-lg mb-2">
            Intellectual property rights and usage terms
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
            <h2>1. Copyright Ownership</h2>
            <h3>1.1 Website Content</h3>
            <p>
              © 2025-2026 Lucid Blocks Wiki. All rights reserved.
            </p>
            <p>
              Unless otherwise noted, all original content on this website, including but not limited to text,
              graphics, logos, guides, articles, and compilations, is the property of Lucid Blocks Wiki and is
              protected by international copyright laws.
            </p>

            <h3>1.2 Game Assets and Trademarks</h3>
            <p>
              Lucid Blocks Wiki is an <strong>unofficial fan-made website</strong> and is NOT affiliated with,
              endorsed by, or associated with:
            </p>
            <ul>
              <li><strong>Steam</strong> - Owner of the Steam platform</li>
              <li><strong>Lucid Blocks Developers</strong> - Creators of the Lucid Blocks game</li>
            </ul>
            <p>
              All game-related content, including but not limited to:
            </p>
            <ul>
              <li>Character images and artwork</li>
              <li>Game screenshots and interface elements</li>
              <li>Game logos and branding</li>
              <li>Character names and abilities</li>
              <li>In-game items and mechanics</li>
            </ul>
            <p>
              ...are the intellectual property of their respective owners. We use such content under the principles
              of fair use for informational, educational, and non-commercial purposes only.
            </p>

            <h2>2. Fair Use Statement</h2>
            <p>
              The use of game assets and copyrighted materials on this website falls under fair use principles as
              outlined in Section 107 of the U.S. Copyright Act. Our use is:
            </p>
            <ul>
              <li><strong>Non-commercial:</strong> We do not directly monetize game assets or content</li>
              <li><strong>Transformative:</strong> We provide guides, analysis, and community resources</li>
              <li><strong>Educational:</strong> We help players learn and understand game mechanics</li>
              <li><strong>Minimal impact:</strong> Our use does not substitute for or harm the original game</li>
            </ul>
            <p>
              We believe our use of copyrighted materials enhances the game experience and serves the community
              without harming the commercial interests of the copyright holders.
            </p>

            <h2>3. User-Generated Content</h2>
            <h3>3.1 Content Submission</h3>
            <p>
              If you submit, post, or contribute content to our website (including but not limited to comments,
              suggestions, guides, or images), you represent and warrant that:
            </p>
            <ul>
              <li>You own or have the necessary rights to the content</li>
              <li>The content does not infringe on any third-party rights</li>
              <li>You grant us a non-exclusive, worldwide, royalty-free license to use, reproduce, modify, and display the content</li>
            </ul>

            <h3>3.2 Content Moderation</h3>
            <p>
              We reserve the right to remove any user-generated content that:
            </p>
            <ul>
              <li>Infringes on copyright or other intellectual property rights</li>
              <li>Violates our Terms of Service</li>
              <li>Contains inappropriate or offensive material</li>
            </ul>

            <h2>4. Trademark Information</h2>
            <p>
              The following trademarks and service marks are the property of their respective owners:
            </p>
            <ul>
              <li><strong>STEAM</strong> - Trademark of Valve Corporation</li>
              <li><strong>Lucid Blocks</strong> - Trademark of the game developers</li>
              <li><strong>Lucid Blocks Wiki</strong> - Our own branding (not affiliated with the game)</li>
            </ul>
            <p>
              All other trademarks, service marks, and trade names referenced on this website are the property of
              their respective owners. The use of any trademark on this website does not imply endorsement or
              affiliation with Lucid Blocks Wiki.
            </p>

            <h2>5. DMCA Policy</h2>
            <h3>5.1 Copyright Infringement Claims</h3>
            <p>
              We respect the intellectual property rights of others and expect our users to do the same. If you
              believe that your copyrighted work has been copied in a way that constitutes copyright infringement
              and is accessible on this website, please notify us.
            </p>

            <h3>5.2 DMCA Takedown Notice</h3>
            <p>
              To file a DMCA takedown notice with us, please provide the following information in writing:
            </p>
            <ul>
              <li>Your physical or electronic signature</li>
              <li>Identification of the copyrighted work you claim has been infringed</li>
              <li>Identification of the material that is claimed to be infringing and information reasonably sufficient to permit us to locate the material</li>
              <li>Your contact information, including your address, telephone number, and email</li>
              <li>A statement that you have a good faith belief that use of the material is not authorized by the copyright owner, its agent, or law</li>
              <li>A statement that the information in the notification is accurate, and under penalty of perjury, that you are authorized to act on behalf of the copyright owner</li>
            </ul>

            <h3>5.3 Counter-Notice</h3>
            <p>
              If you believe that your content was wrongly removed due to a DMCA notice, you may submit a counter-notice
              containing:
            </p>
            <ul>
              <li>Your physical or electronic signature</li>
              <li>Identification of the removed material and its location before removal</li>
              <li>A statement under penalty of perjury that you have a good faith belief that the material was removed as a result of mistake or misidentification</li>
              <li>Your name, address, and telephone number, and a statement that you consent to jurisdiction in your district</li>
            </ul>

            <h3>5.4 Copyright Agent Contact</h3>
            <p>
              Please send all DMCA notices and counter-notices to:
            </p>
            <p>
              <strong>DMCA Agent</strong><br />
              Lucid Blocks Wiki<br />
              Email: <a href="mailto:dmca@lucidblocks.wiki" className="text-[hsl(var(--nav-theme-light))] hover:underline">dmca@lucidblocks.wiki</a>
            </p>
            <p>
              <strong>Note:</strong> Please allow up to 7 business days for a response. Misrepresentation in a
              DMCA notice or counter-notice may result in legal liability.
            </p>

            <h2>6. Restrictions on Use</h2>
            <h3>6.1 Prohibited Uses</h3>
            <p>
              You may NOT:
            </p>
            <ul>
              <li>Reproduce, duplicate, or copy material from our website for commercial purposes without written permission</li>
              <li>Redistribute our original content on other websites or platforms without attribution</li>
              <li>Use automated tools (bots, scrapers) to collect or copy content from our website</li>
              <li>Remove or alter any copyright notices or attributions</li>
              <li>Claim ownership of our original content</li>
            </ul>

            <h3>6.2 Permitted Uses</h3>
            <p>
              You MAY:
            </p>
            <ul>
              <li>View and access content for personal, non-commercial use</li>
              <li>Share links to our pages on social media or forums</li>
              <li>Quote brief excerpts with proper attribution and a link back to our website</li>
              <li>Use content for educational purposes with proper credit</li>
            </ul>

            <h2>7. Attribution Requirements</h2>
            <p>
              If you wish to use or reference our original content (guides, articles, data compilations), please:
            </p>
            <ul>
              <li>Provide clear attribution to "Lucid Blocks Wiki"</li>
              <li>Include a link back to the original page (if digital)</li>
              <li>Do not imply endorsement or affiliation</li>
            </ul>
            <p>
              Example attribution: <em>"Source: Lucid Blocks Wiki (lucidblocks.wiki)"</em>
            </p>

            <h2>8. Repeat Infringer Policy</h2>
            <p>
              In accordance with the DMCA and other applicable laws, we have adopted a policy of terminating, in
              appropriate circumstances and at our sole discretion, access to the website for users who are deemed
              to be repeat infringers.
            </p>

            <h2>9. International Copyright</h2>
            <p>
              Our website is accessible worldwide. We comply with U.S. copyright law, but we also respect international
              copyright treaties and conventions. If you believe content on our website violates copyright laws in your
              jurisdiction, please contact us using the information below.
            </p>

            <h2>10. Changes to This Notice</h2>
            <p>
              We reserve the right to update this Copyright Notice at any time. Changes will be effective immediately
              upon posting to the website. The "Last Updated" date at the top of this page indicates when the notice
              was last revised.
            </p>

            <h2>11. No Legal Advice</h2>
            <p>
              This Copyright Notice is provided for informational purposes only and does not constitute legal advice.
              For specific legal questions or concerns, please consult with a qualified attorney.
            </p>

            <h2>12. Contact Information</h2>
            <p>
              For copyright questions, licensing inquiries, or to report copyright infringement:
            </p>
            <p>
              <strong>General Inquiries:</strong> <a href="mailto:copyright@lucidblocks.wiki" className="text-[hsl(var(--nav-theme-light))] hover:underline">copyright@lucidblocks.wiki</a><br />
              <strong>DMCA Notices:</strong> <a href="mailto:dmca@lucidblocks.wiki" className="text-[hsl(var(--nav-theme-light))] hover:underline">dmca@lucidblocks.wiki</a>
            </p>
            <p>
              We aim to respond to all legitimate inquiries within 7 business days.
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

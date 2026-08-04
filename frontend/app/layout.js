import "./globals.css";
import Script from "next/script";
import Header from "../components/Header";
import PwaRegister from "../components/PwaRegister";
import SubscribePopup from "../components/SubscribePopup";
import MobileNav from "../components/MobileNav";
import { SITE_URL, SITE_NAME, SITE_ALT_NAMES } from "../lib/site";

const DESCRIPTION =
  "O'zbekistonda biznes ochish va yuritish bo'yicha amaliy darslar — jahon tajribasi asosida, o'zbek tilida. Biznesni boshlash, moliya, marketing, sotuv, boshqaruv va onlayn biznes.";

const GA_ID = process.env.NEXT_PUBLIC_GA_ID || "G-BZNDRSLR26";

export const metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: `${SITE_NAME} — O'zbekistonda biznes ochish va yuritishni o'rganing`,
    template: `%s — ${SITE_NAME}`,
  },
  description: DESCRIPTION,
  applicationName: SITE_NAME,
  verification: {
    google: "jEeD26Njx-UkuDnHIGe8CH5eoTfU03l1f1HSn934j9Y",
  },

  alternates: {
    canonical: "/",
    types: {
      "application/rss+xml": [
        { url: "/api/news/rss", title: `${SITE_NAME} RSS` },
      ],
    },
  },
  openGraph: {
    type: "website",
    url: "/",
    siteName: SITE_NAME,
    locale: "uz_UZ",
    title: `${SITE_NAME} — O'zbekistonda biznes ochish va yuritishni o'rganing`,
    description: DESCRIPTION,
  },
  twitter: {
    card: "summary_large_image",
    title: `${SITE_NAME} — Amaliy biznes darslari`,
    description: DESCRIPTION,
  },
  appleWebApp: {
    capable: true,
    title: SITE_NAME,
    statusBarStyle: "black-translucent",
  },
};

const siteJsonLd = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "@id": `${SITE_URL}/#organization`,
      name: SITE_NAME,
      alternateName: SITE_ALT_NAMES,
      url: SITE_URL,
      logo: {
        "@type": "ImageObject",
        url: `${SITE_URL}/icon-512`,
        width: 512,
        height: 512,
      },
      sameAs: ["https://t.me/biznesxabari"],
    },
    {
      "@type": "WebSite",
      "@id": `${SITE_URL}/#website`,
      name: SITE_NAME,
      alternateName: SITE_ALT_NAMES,
      url: SITE_URL,
      inLanguage: "uz",
      publisher: { "@id": `${SITE_URL}/#organization` },
      potentialAction: {
        "@type": "SearchAction",
        target: {
          "@type": "EntryPoint",
          urlTemplate: `${SITE_URL}/qidiruv?q={search_term_string}`,
        },
        "query-input": "required name=search_term_string",
      },
    },
  ],
};

export const viewport = {
  themeColor: "#0f172a",
};

export default function RootLayout({ children }) {
  return (
    <html lang="uz">
      <head>
        {/* Google Analytics 4 (GA4) Script */}
        <Script
          strategy="afterInteractive"
          src={`https://www.googletagmanager.com/gtag/js?id=${GA_ID}`}
        />
        <Script
          id="google-analytics"
          strategy="afterInteractive"
          dangerouslySetInnerHTML={{
            __html: `
              window.dataLayer = window.dataLayer || [];
              function gtag(){dataLayer.push(arguments);}
              gtag('js', new Date());
              gtag('config', '${GA_ID}', {
                page_path: window.location.pathname,
              });
            `,
          }}
        />
      </head>
      <body>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(siteJsonLd) }}
        />
        <Header />
        <main className="mx-auto max-w-6xl px-4 pb-24 md:pb-16">{children}</main>
        <footer className="border-t border-slate-800 py-8 text-center text-sm text-slate-500">
          <div className="mb-3 flex justify-center gap-4 flex-wrap">
            <a href="/kalkulyator" className="text-amber-400 font-semibold hover:underline">
              🧮 Biznes Kalkulyatori
            </a>
            <span>•</span>
            <a href="/hamkorlik" className="text-slate-400 hover:text-white transition-colors">
              🤝 B2B Hamkorlik
            </a>
            <span>•</span>
            <a href="/haqida" className="text-slate-400 hover:text-white transition-colors">
              Biz haqimizda
            </a>
            <span>•</span>
            <a href="/aloqa" className="text-slate-400 hover:text-white transition-colors">
              Aloqa
            </a>
            <span>•</span>
            <a href="/maxfiylik" className="text-slate-400 hover:text-white transition-colors">
              Maxfiylik
            </a>
            <span>•</span>
            <a
              href="https://t.me/biznesxabari"
              target="_blank"
              rel="noopener noreferrer"
              className="text-slate-400 hover:text-sky-400 transition-colors"
            >
              📢 Telegram Kanal (@biznesxabari)
            </a>
          </div>
          © {new Date().getFullYear()} Biznes Darslari (biznesdarslari.uz) — O&apos;zbekistonda biznes ochish va yuritish bo&apos;yicha amaliy darslar
        </footer>
        <MobileNav />
        <SubscribePopup />
        <PwaRegister />
      </body>
    </html>
  );
}

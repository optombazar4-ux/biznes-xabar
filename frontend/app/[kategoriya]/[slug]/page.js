import Link from "next/link";
import { permanentRedirect } from "next/navigation";
import MarkdownContent from "../../../components/MarkdownContent";
import MarkRead from "../../../components/MarkRead";
import { apiGet } from "../../../lib/api";
import { SITE_URL, SITE_NAME } from "../../../lib/site";
import { readingMinutes, levelForCategory, formatDate } from "../../../lib/lesson";

export async function generateMetadata({ params }) {
  const { kategoriya, slug } = await params;
  const article = await apiGet(`/api/news/${slug}`);
  if (!article) return { title: "Dars topilmadi" };

  const title = article.seo_title || article.title;
  const catSlug = article.category?.slug || kategoriya;
  const url = `/${catSlug}/${article.slug}`;

  return {
    title,
    description: article.summary,
    keywords: article.tags || [],
    alternates: { canonical: url },
    openGraph: {
      type: "article",
      url,
      siteName: SITE_NAME,
      locale: "uz_UZ",
      title,
      description: article.summary,
      publishedTime: article.published_at || article.created_at,
      section: article.category?.name,
      tags: article.tags || [],
    },
    twitter: {
      card: "summary_large_image",
      title,
      description: article.summary,
    },
  };
}

function jsonLd(article, catSlug) {
  const url = `${SITE_URL}/${catSlug}/${article.slug}`;
  const articleLd = {
    "@context": "https://schema.org",
    "@type": "Article",
    mainEntityOfPage: { "@type": "WebPage", "@id": url },
    headline: article.title,
    description: article.summary,
    image: [
      article.image_url?.startsWith("http") ? article.image_url : `${url}/opengraph-image`,
    ],
    datePublished: article.published_at || article.created_at,
    dateModified: article.published_at || article.created_at,
    inLanguage: "uz",
    articleSection: article.category?.name,
    keywords: (article.tags || []).join(", "),
    author: { "@type": "Organization", name: SITE_NAME, url: SITE_URL },
    publisher: { "@id": `${SITE_URL}/#organization` },
  };
  const breadcrumbLd = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: [
      { "@type": "ListItem", position: 1, name: "Bosh sahifa", item: SITE_URL },
      article.category && {
        "@type": "ListItem",
        position: 2,
        name: article.category.name,
        item: `${SITE_URL}/${catSlug}`,
      },
      { "@type": "ListItem", position: 3, name: article.title, item: url },
    ].filter(Boolean),
  };
  return [articleLd, breadcrumbLd];
}

export default async function LessonPage({ params }) {
  const { kategoriya, slug } = await params;
  const article = await apiGet(`/api/news/${slug}`);

  if (!article) {
    return (
      <div className="py-20 text-center text-slate-400">
        Dars topilmadi. <Link href="/" className="text-amber-400">Bosh sahifaga qaytish</Link>
      </div>
    );
  }

  const catSlug = article.category?.slug || kategoriya;
  // Kanonik URL — noto'g'ri bo'lim orqali kelinsa, to'g'ri manzilga yo'naltiramiz
  if (article.category?.slug && kategoriya !== article.category.slug) {
    permanentRedirect(`/${article.category.slug}/${slug}`);
  }

  const date = formatDate(article.published_at);
  const minutes = readingMinutes(article.content);
  const level = levelForCategory(article.category?.slug);
  const shareUrl = `https://t.me/share/url?url=${encodeURIComponent(`${SITE_URL}/${catSlug}/${article.slug}`)}&text=${encodeURIComponent(article.title)}`;

  // Kursdagi oldingi/keyingi dars
  let prev = null;
  let next = null;
  if (article.category?.slug) {
    const siblings =
      (await apiGet("/api/news", {
        kategoriya: article.category.slug,
        tartib: "kurs",
        limit: 100,
      })) || [];
    const idx = siblings.findIndex((a) => a.slug === article.slug);
    if (idx !== -1) {
      prev = idx > 0 ? siblings[idx - 1] : null;
      next = idx < siblings.length - 1 ? siblings[idx + 1] : null;
    }
  }

  return (
    <article className="mx-auto max-w-3xl py-8">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd(article, catSlug)) }}
      />
      <MarkRead slug={article.slug} />

      <div className="mb-3 flex flex-wrap items-center gap-3 text-sm text-slate-400">
        {article.category && (
          <Link
            href={`/${catSlug}`}
            className="rounded-full bg-amber-500/10 px-3 py-1 font-semibold text-amber-400"
          >
            {article.category.name}
          </Link>
        )}
        <span>{level}</span>
        <span>⏱ {minutes} daqiqa</span>
        {date && <span>{date}</span>}
      </div>

      <h1 className="mb-4 text-3xl font-bold leading-tight">{article.title}</h1>

      {article.image_url && (
        // eslint-disable-next-line @next/next/no-img-element
        <img src={article.image_url} alt="" className="mb-6 w-full rounded-xl object-cover" />
      )}

      <p className="mb-6 border-l-4 border-amber-500 pl-4 text-lg leading-relaxed text-slate-200">
        {article.summary}
      </p>

      <div className="prose-invert mb-6">
        <MarkdownContent content={article.content} />
      </div>

      {article.practical_note && (
        <div className="mb-6 rounded-xl border border-amber-900 bg-amber-500/5 p-5">
          <div className="mb-1 text-sm font-bold text-amber-400">💡 BU NIMA DEGANI?</div>
          <p className="text-slate-200">{article.practical_note}</p>
        </div>
      )}

      <div className="mb-6 flex flex-wrap gap-2">
        {(article.tags || []).map((tag) => (
          <Link
            key={tag}
            href={`/qidiruv?q=${encodeURIComponent(tag)}`}
            className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300 hover:bg-amber-600 hover:text-white"
          >
            #{tag}
          </Link>
        ))}
      </div>

      {/* Ogohlantirish — moliyaviy/huquqiy mas'uliyat */}
      <div className="mb-6 rounded-xl border border-slate-800 bg-slate-900/50 p-4 text-xs leading-relaxed text-slate-400">
        <strong className="text-slate-300">Ogohlantirish:</strong> Ushbu dars umumiy
        ma&apos;lumot va ta&apos;lim maqsadida tayyorlangan. Soliq, qonun va moliyaviy
        qarorlar bo&apos;yicha aniq holatingiz uchun rasmiy manbalar (soliq.uz, lex.uz) yoki
        malakali mutaxassis bilan maslahatlashing.
      </div>

      {/* Muallif / yangilanish */}
      <div className="mb-6 flex flex-wrap items-center gap-2 border-t border-slate-800 pt-5 text-sm text-slate-400">
        <span className="text-lg">🎓</span>
        <span className="font-semibold text-slate-200">Biznes Darslari jamoasi</span>
        {date && <span>· Yangilangan: {date}</span>}
      </div>

      {/* Oldingi / keyingi dars */}
      {(prev || next) && (
        <nav className="mb-6 grid gap-3 sm:grid-cols-2">
          {prev ? (
            <Link
              href={`/${catSlug}/${prev.slug}`}
              className="rounded-xl border border-slate-800 p-4 transition hover:border-amber-600"
            >
              <div className="text-xs text-slate-500">← Oldingi dars</div>
              <div className="mt-1 line-clamp-2 text-sm font-medium">{prev.title}</div>
            </Link>
          ) : (
            <span />
          )}
          {next && (
            <Link
              href={`/${catSlug}/${next.slug}`}
              className="rounded-xl border border-amber-600/60 bg-amber-500/5 p-4 text-right transition hover:border-amber-500"
            >
              <div className="text-xs text-amber-400">Keyingi dars →</div>
              <div className="mt-1 line-clamp-2 text-sm font-medium">{next.title}</div>
            </Link>
          )}
        </nav>
      )}

      <div className="flex flex-wrap items-center gap-4 border-t border-slate-800 pt-5 text-sm">
        {article.category && (
          <Link
            href={`/${catSlug}`}
            className="rounded-lg border border-slate-700 px-3 py-1.5 text-slate-200 hover:border-amber-500"
          >
            ← Kursga qaytish
          </Link>
        )}
        <a
          href={shareUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="rounded-lg bg-sky-600 px-3 py-1.5 text-white hover:bg-sky-500"
        >
          📤 Telegramda ulashish
        </a>
      </div>
    </article>
  );
}

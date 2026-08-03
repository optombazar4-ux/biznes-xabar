import { notFound } from "next/navigation";
import IdeaList from "../../../components/IdeaList";
import { apiGet } from "../../../lib/api";
import { readingMinutes } from "../../../lib/lesson";
import { SITE_URL } from "../../../lib/site";

const INTENTS = {
  "5-mln-gacha": {
    name: "5 mln so'm gacha biznes g'oyalari",
    title: "5 mln so'm budjet bilan boshlanadigan biznes g'oyalari — O'zbekistonda 2026",
    description: "Kichik kapital va minimal xavf bilan 5 million so'mgacha bo'lgan budjetda O'zbekistonda boshlash mumkin bo'lgan amaliy biznes g'oyalari va 7 kunlik sinov rejasi.",
    filter: "5 mln gacha",
  },
  uydan: {
    name: "Uyda qilinadigan biznes g'oyalari",
    title: "Uy sharoitida qilinadigan ayollar va yoshlar uchun biznes g'oyalari",
    description: "Ijaraga va katta ofisga xarajat qilmasdan, uyda o'tirib daromad keltiruvchi amaliy biznes g'oyalari va bosqichma-bosqich yo'riqnomalar.",
    filter: "uydan",
  },
  qishloq: {
    name: "Qishloqda biznes g'oyalari",
    title: "Qishloq va tumanlar uchun daromadli va moslashtirilgan biznes g mezonlari",
    description: "Tuman va qishloq sharoitida qishloq xo'jaligi, mahsulotlarni qadoqlash va mahalliy xizmatlar bo'yicha amaliy biznes g'oyalari.",
    filter: "qishloq",
  },
  onlayn: {
    name: "Onlayn va internet biznes g'oyalari",
    title: "Internet orqali onlayn daromad va digital biznes g'oyalari",
    description: "Uzum Market, ijtimoiy tarmoqlar va masofaviy xizmatlar orqali onlayn biznes boshlash yo'riqnomalari.",
    filter: "onlayn",
  },
  xizmat: {
    name: "Xizmat ko'rsatish biznes g'oyalari",
    title: "Xizmat ko'rsatish sohasidagi daromadli biznes g'oyalari",
    description: "Katta tovar zaxirasisiz xizmat ko'rsatish orqali yuqori marja bilan ishlaydigan biznes modellar.",
    filter: "xizmat",
  },
  savdo: {
    name: "Savdo va riteyl biznes g'oyalari",
    title: "Savdo va do'kon ochish bo'yicha amaliy biznes g'oyalari",
    description: "Mahalliy va onlayn savdo, tez sotiladigan tovarlar va distribyutsiya biznes g'oyalari.",
    filter: "savdo",
  },
  "ishlab-chiqarish": {
    name: "Kichik ishlab chiqarish g'oyalari",
    title: "Kichik minitsexdan sexgacha: ishlab chiqarish biznes g'oyalari",
    description: "Xomashyoni qayta ishlash, qadoqlash va mini ishlab chiqarish liniyalarini yo'lga qo'yish g'oyalari.",
    filter: "ishlab chiqarish",
  },
};

export async function generateStaticParams() {
  return Object.keys(INTENTS).map((intent) => ({ intent }));
}

export async function generateMetadata({ params }) {
  const { intent } = await params;
  const config = INTENTS[intent];
  if (!config) return { title: "Sahifa topilmadi" };

  return {
    title: config.title,
    description: config.description,
    alternates: { canonical: `/biznes-goyalari/${intent}` },
    openGraph: {
      title: config.title,
      description: config.description,
      url: `/biznes-goyalari/${intent}`,
    },
  };
}

export default async function IntentPage({ params }) {
  const { intent } = await params;
  const config = INTENTS[intent];
  if (!config) notFound();

  const articles = (await apiGet("/api/news", { kategoriya: "biznes-goyalari", q: config.filter, limit: 100 })) || [];
  const lessons = articles.map((a) => ({
    slug: a.slug,
    title: a.title,
    summary: a.summary,
    tags: a.tags,
    minutes: readingMinutes(a.content),
  }));

  const breadcrumbLd = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: [
      { "@type": "ListItem", position: 1, name: "Bosh sahifa", item: SITE_URL },
      { "@type": "ListItem", position: 2, name: "Biznes g'oyalari", item: `${SITE_URL}/biznes-goyalari` },
      { "@type": "ListItem", position: 3, name: config.name, item: `${SITE_URL}/biznes-goyalari/${intent}` },
    ],
  };

  return (
    <div className="mx-auto max-w-6xl py-8">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbLd) }}
      />
      <p className="mb-1 text-sm font-semibold uppercase tracking-wide text-amber-400">
        💡 SEO Intent Hub · {config.name}
      </p>
      <h1 className="mb-3 text-2xl sm:text-3xl font-bold leading-tight">
        {config.title}
      </h1>
      <p className="mb-8 leading-relaxed text-slate-300 border-l-4 border-amber-500 pl-4 bg-slate-900/40 py-3 pr-3 rounded-r-xl">
        {config.description}
      </p>

      {lessons.length > 0 ? (
        <IdeaList ideas={lessons} />
      ) : (
        <p className="text-slate-400">Ushbu yo&apos;nalishda g&apos;oyalar yuklanmoqda.</p>
      )}
    </div>
  );
}

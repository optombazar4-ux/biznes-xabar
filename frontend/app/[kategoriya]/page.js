import { notFound } from "next/navigation";
import CourseList from "../../components/CourseList";
import IdeaList from "../../components/IdeaList";
import { apiGet } from "../../lib/api";
import { readingMinutes } from "../../lib/lesson";
import { SITE_URL } from "../../lib/site";

async function getCategory(slug) {
  const categories = (await apiGet("/api/categories")) || [];
  return categories.find((c) => c.slug === slug) || null;
}

export async function generateMetadata({ params }) {
  const { kategoriya } = await params;
  const category = await getCategory(kategoriya);
  if (!category) return { title: "Bo'lim topilmadi" };
  const name = category.name;

  return {
    title: `${name} — biznes darslari kursi`,
    description: `${name} bo'yicha amaliy biznes darslari kursi — bosqichma-bosqich, O'zbekiston sharoitiga moslashtirilgan.`,
    alternates: { canonical: `/${kategoriya}` },
    openGraph: {
      title: `${name} — biznes darslari kursi`,
      description: `${name} bo'yicha bosqichma-bosqich biznes darslari — o'zbek tilida.`,
      url: `/${kategoriya}`,
    },
  };
}

export default async function CoursePage({ params }) {
  const { kategoriya } = await params;
  const category = await getCategory(kategoriya);
  if (!category) notFound();

  const articles =
    (await apiGet("/api/news", { kategoriya, tartib: "kurs", limit: 100 })) || [];
  const lessons = articles.map((a) => ({
    slug: a.slug,
    title: a.title,
    summary: a.summary,
    tags: a.tags,
    minutes: readingMinutes(a.content),
  }));
  const isIdeas = kategoriya === "biznes-goyalari";

  const breadcrumbLd = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: [
      { "@type": "ListItem", position: 1, name: "Bosh sahifa", item: SITE_URL },
      { "@type": "ListItem", position: 2, name: category.name, item: `${SITE_URL}/${kategoriya}` },
    ],
  };

  return (
    <div className="mx-auto max-w-6xl py-8">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbLd) }}
      />
      <p className="mb-1 text-sm font-semibold uppercase tracking-wide text-amber-400">
        {isIdeas ? "Amaliy g'oyalar katalogi" : "O'quv yo'nalishi"}
      </p>
      <h1 className="mb-3 text-2xl font-bold">
        {isIdeas ? "💡" : "📂"} {category.name}
      </h1>
      {isIdeas && (
        <p className="mb-6 max-w-2xl leading-relaxed text-slate-400">
          Budjetingiz, ishlash joyingiz va biznes turiga mos g&apos;oyani tanlang.
          Har bir g&apos;oyada boshlang&apos;ich xarajat, mijoz, daromad modeli,
          7 kunlik sinov rejasi va asosiy xavflar ko&apos;rsatiladi.
        </p>
      )}

      {lessons.length > 0 ? (
        isIdeas ? (
          <IdeaList ideas={lessons} />
        ) : (
          <CourseList lessons={lessons} categorySlug={kategoriya} />
        )
      ) : (
        <p className="text-slate-400">Bu bo&apos;limda hali darslar yo&apos;q.</p>
      )}
    </div>
  );
}

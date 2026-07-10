import { notFound } from "next/navigation";
import CourseList from "../../components/CourseList";
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
    minutes: readingMinutes(a.content),
  }));

  const breadcrumbLd = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: [
      { "@type": "ListItem", position: 1, name: "Bosh sahifa", item: SITE_URL },
      { "@type": "ListItem", position: 2, name: category.name, item: `${SITE_URL}/${kategoriya}` },
    ],
  };

  return (
    <div className="mx-auto max-w-3xl py-8">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbLd) }}
      />
      <p className="mb-1 text-sm font-semibold uppercase tracking-wide text-amber-400">
        O&apos;quv yo&apos;nalishi
      </p>
      <h1 className="mb-6 text-2xl font-bold">📂 {category.name}</h1>

      {lessons.length > 0 ? (
        <CourseList lessons={lessons} categorySlug={kategoriya} />
      ) : (
        <p className="text-slate-400">Bu bo&apos;limda hali darslar yo&apos;q.</p>
      )}
    </div>
  );
}

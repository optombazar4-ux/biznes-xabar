import CourseList from "../../../components/CourseList";
import { apiGet } from "../../../lib/api";
import { readingMinutes } from "../../../lib/lesson";

export async function generateMetadata({ params }) {
  const { slug } = await params;
  const categories = (await apiGet("/api/categories")) || [];
  const category = categories.find((c) => c.slug === slug);
  const name = category?.name || slug;

  return {
    title: `${name} — biznes darslari kursi`,
    description: `${name} bo'yicha amaliy biznes darslari kursi — bosqichma-bosqich, O'zbekiston sharoitiga moslashtirilgan.`,
    alternates: { canonical: `/kategoriya/${slug}` },
    openGraph: {
      title: `${name} — biznes darslari kursi`,
      description: `${name} bo'yicha bosqichma-bosqich biznes darslari — o'zbek tilida.`,
      url: `/kategoriya/${slug}`,
    },
  };
}

export default async function CategoryPage({ params }) {
  const { slug } = await params;
  const [articles, categories] = await Promise.all([
    apiGet("/api/news", { kategoriya: slug, tartib: "kurs", limit: 100 }),
    apiGet("/api/categories"),
  ]);
  const category = (categories || []).find((c) => c.slug === slug);

  const lessons = (articles || []).map((a) => ({
    slug: a.slug,
    title: a.title,
    minutes: readingMinutes(a.content),
  }));

  return (
    <div className="mx-auto max-w-3xl py-8">
      <p className="mb-1 text-sm font-semibold uppercase tracking-wide text-amber-400">
        O&apos;quv yo&apos;nalishi
      </p>
      <h1 className="mb-6 text-2xl font-bold">📂 {category?.name || slug}</h1>

      {lessons.length > 0 ? (
        <CourseList lessons={lessons} />
      ) : (
        <p className="text-slate-400">Bu bo&apos;limda hali darslar yo&apos;q.</p>
      )}
    </div>
  );
}

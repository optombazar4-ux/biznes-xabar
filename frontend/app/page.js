import Link from "next/link";
import ArticleCard from "../components/ArticleCard";
import AdPlaceholder from "../components/AdPlaceholder";
import { apiGet } from "../lib/api";

// Har bir kurikulum bo'limi uchun ikonka
const SECTION_ICONS = {
  "biznesni-boshlash": "🚀",
  moliya: "💰",
  "marketing-sotuv": "📣",
  boshqaruv: "👥",
  "onlayn-biznes": "🛒",
  "amaliy-konikmalar": "🎯",
};

export default async function HomePage() {
  const [latest, categories, trends] = await Promise.all([
    apiGet("/api/news", { limit: 12 }),
    apiGet("/api/categories"),
    apiGet("/api/news/trends"),
  ]);

  const hasLessons = (latest || []).length > 0;

  return (
    <div className="py-8">
      {/* Hero */}
      <section className="mb-10 rounded-2xl border border-slate-800 bg-gradient-to-br from-amber-950/40 to-slate-900 p-8 text-center">
        <h1 className="mx-auto max-w-2xl text-2xl font-bold leading-tight sm:text-3xl">
          O&apos;zbekistonda biznes ochish va yuritishni o&apos;rganing
        </h1>
        <p className="mx-auto mt-3 max-w-2xl leading-relaxed text-slate-300">
          Jahon tajribasi asosida tayyorlangan amaliy biznes darslari — biznesni boshlash,
          moliya, marketing, sotuv, boshqaruv va onlayn biznes bo&apos;yicha.
        </p>
      </section>

      <div className="grid gap-8 lg:grid-cols-[1fr_300px]">
        <div>
          {/* Bo'limlar */}
          {(categories || []).length > 0 && (
            <section className="mb-10">
              <h2 className="mb-4 text-xl font-bold">📚 Bo&apos;limlar</h2>
              <div className="grid gap-4 sm:grid-cols-2">
                {categories.map((cat) => (
                  <Link
                    key={cat.slug}
                    href={`/kategoriya/${cat.slug}`}
                    className="flex items-center gap-3 rounded-xl border border-slate-800 bg-slate-900/60 p-4 transition hover:border-amber-600"
                  >
                    <span className="text-3xl">{SECTION_ICONS[cat.slug] || "📘"}</span>
                    <span className="font-semibold">{cat.name}</span>
                  </Link>
                ))}
              </div>
            </section>
          )}

          {/* So'nggi darslar */}
          <section>
            <h2 className="mb-4 text-xl font-bold">🆕 So&apos;nggi darslar</h2>
            {hasLessons ? (
              <div className="grid gap-5 sm:grid-cols-2">
                {latest.map((article) => (
                  <ArticleCard key={article.id} article={article} />
                ))}
              </div>
            ) : (
              <div className="rounded-xl border border-slate-800 p-10 text-center leading-relaxed text-slate-400">
                Darslar tez orada qo&apos;shiladi. Backend&apos;da{" "}
                <code className="rounded bg-slate-800 px-2 py-0.5">python -m app.pipeline</code>{" "}
                buyrug&apos;ini ishga tushiring.
              </div>
            )}
          </section>
        </div>

        <aside className="space-y-8">
          <section>
            <AdPlaceholder type="sidebar" />
          </section>

          <section>
            <h2 className="mb-3 font-bold">🔖 Ommabop mavzular</h2>
            <div className="flex flex-wrap gap-2">
              {(trends || []).length > 0 ? (
                trends.map((trend) => (
                  <Link
                    key={trend.teg}
                    href={`/qidiruv?q=${encodeURIComponent(trend.teg)}`}
                    className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300 hover:bg-amber-600 hover:text-white"
                  >
                    #{trend.teg}
                  </Link>
                ))
              ) : (
                <p className="text-sm text-slate-500">Teglar hali shakllanmadi.</p>
              )}
            </div>
          </section>
        </aside>
      </div>
    </div>
  );
}

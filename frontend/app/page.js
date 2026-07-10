import Link from "next/link";
import ArticleCard from "../components/ArticleCard";
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

// Foydalanuvchi turini tanlash — maqsadga qarab tegishli bo'limga yo'naltiradi
const USER_GOALS = [
  { label: "Biznes boshlamoqchiman", emoji: "🚀", slug: "biznesni-boshlash" },
  { label: "Sotuvni oshirmoqchiman", emoji: "📣", slug: "marketing-sotuv" },
  { label: "Moliyani tartibga solmoqchiman", emoji: "💰", slug: "moliya" },
];

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
      <section className="mb-8 rounded-2xl border border-slate-800 bg-gradient-to-br from-amber-950/40 to-slate-900 p-8 text-center">
        <h1 className="mx-auto max-w-2xl text-2xl font-bold leading-tight sm:text-3xl">
          O&apos;zbekistonda biznes ochish va yuritishni o&apos;rganing
        </h1>
        <p className="mx-auto mt-3 max-w-2xl leading-relaxed text-slate-300">
          Jahon tajribasi asosida tayyorlangan amaliy biznes darslari — biznesni boshlash,
          moliya, marketing, sotuv, boshqaruv va onlayn biznes bo&apos;yicha.
        </p>
        <Link
          href="/kategoriya/biznesni-boshlash"
          className="mt-6 inline-block rounded-xl bg-amber-500 px-6 py-3 font-bold text-slate-950 transition hover:bg-amber-400"
        >
          🎓 Bepul o&apos;rganishni boshlash
        </Link>
      </section>

      {/* Foydalanuvchi maqsadi */}
      <section className="mb-10">
        <p className="mb-3 text-center text-sm text-slate-400">Nimadan boshlaymiz?</p>
        <div className="grid gap-3 sm:grid-cols-3">
          {USER_GOALS.map((goal) => (
            <Link
              key={goal.slug}
              href={`/kategoriya/${goal.slug}`}
              className="flex items-center gap-3 rounded-xl border border-slate-800 bg-slate-900/60 px-4 py-3 text-sm font-medium transition hover:border-amber-500 hover:bg-slate-900"
            >
              <span className="text-2xl">{goal.emoji}</span>
              <span>{goal.label}</span>
            </Link>
          ))}
        </div>
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

import Link from "next/link";
import ArticleCard from "../components/ArticleCard";
import TelegramBanner from "../components/TelegramBanner";
import SmartMatcher from "../components/SmartMatcher";
import { apiGet } from "../lib/api";

// Har bir kurikulum bo'limi uchun ikonka
const SECTION_ICONS = {
  "biznes-goyalari": "💡",
  "biznesni-boshlash": "🚀",
  moliya: "💰",
  "marketing-sotuv": "📣",
  boshqaruv: "👥",
  "onlayn-biznes": "🛒",
  "amaliy-konikmalar": "🎯",
};

// Foydalanuvchi turini tanlash — maqsadga qarab tegishli bo'limga yo'naltiradi
const USER_GOALS = [
  { label: "Menga biznes g'oya kerak", emoji: "💡", slug: "biznes-goyalari" },
  { label: "Biznes boshlamoqchiman", emoji: "🚀", slug: "biznesni-boshlash" },
  { label: "Sotuvni oshirmoqchiman", emoji: "📣", slug: "marketing-sotuv" },
  { label: "Moliyani tartibga solmoqchiman", emoji: "💰", slug: "moliya" },
];

export default async function HomePage() {
  const [latest, categories, trends, stats] = await Promise.all([
    apiGet("/api/news", { limit: 12 }),
    apiGet("/api/categories"),
    apiGet("/api/news/trends"),
    apiGet("/api/news/stats"),
  ]);

  const hasLessons = (latest || []).length > 0;
  // Haqiqiy sonlar API'dan kelmasa statik reklama raqamlariga tushamiz
  const totalLessons = stats?.jami_darslar || 0;
  const totalIdeas = stats?.biznes_goyalar || 0;

  return (
    <div className="py-6 space-y-10">
      {/* Hero */}
      <section className="relative overflow-hidden rounded-3xl border border-slate-800/80 bg-gradient-to-br from-amber-950/40 via-slate-900/90 to-slate-950 p-8 sm:p-12 text-center shadow-2xl">
        <div className="absolute top-0 right-1/2 translate-x-1/2 -mt-12 h-40 w-96 rounded-full bg-amber-500/10 blur-3xl pointer-events-none" />
        
        <div className="inline-flex items-center gap-2 rounded-full border border-amber-500/30 bg-amber-500/10 px-3.5 py-1 text-xs font-bold text-amber-400 mb-4 shadow-sm backdrop-blur-md">
          <span className="flex h-2 w-2 rounded-full bg-amber-400 animate-pulse" />
          <span>O'zbekiston uchun #1 Bepul Biznes Ta'lim Platformasi</span>
        </div>

        <h1 className="mx-auto max-w-3xl text-2xl font-black tracking-tight leading-tight sm:text-4xl lg:text-5xl text-white">
          O'zbekistonda biznes ochish va yuritishni <span className="bg-gradient-to-r from-amber-400 via-amber-300 to-amber-500 bg-clip-text text-transparent">noldan o'rganing</span>
        </h1>
        <p className="mx-auto mt-4 max-w-2xl text-slate-300 text-sm sm:text-base leading-relaxed">
          113+ ta amaliy bepul darslar, soliq va huquqiy yo'riqnomalar, moliyaviy kalkulyatorlar hamda 75+ verifikatsiya qilingan biznes g'oyalari.
        </p>

        {/* Quick Stats Badges */}
        <div className="mt-8 flex flex-wrap items-center justify-center gap-3 text-xs sm:text-sm font-semibold text-slate-300">
          <div className="flex items-center gap-2 rounded-xl border border-slate-800 bg-slate-900/80 px-4 py-2 backdrop-blur-sm">
            <span className="text-amber-400 text-base">📚</span>
            <span>{totalLessons ? `${totalLessons}+ Amaliy Dars` : "113+ Amaliy Dars"}</span>
          </div>
          <div className="flex items-center gap-2 rounded-xl border border-slate-800 bg-slate-900/80 px-4 py-2 backdrop-blur-sm">
            <span className="text-amber-400 text-base">💡</span>
            <span>{totalIdeas ? `${totalIdeas}+ Biznes G'oya` : "75+ Biznes G'oya"}</span>
          </div>
          <div className="flex items-center gap-2 rounded-xl border border-slate-800 bg-slate-900/80 px-4 py-2 backdrop-blur-sm">
            <span className="text-amber-400 text-base">🧮</span>
            <span>Moliyaviy Kalkulyator</span>
          </div>
        </div>
      </section>

      {/* AI Smart Business Matcher */}
      <section>
        <SmartMatcher />
      </section>

      {/* Telegram Obuna Banneri */}
      <TelegramBanner />

      {/* Foydalanuvchi maqsadi */}
      <section className="mb-10">
        <div className="mb-4 text-center">
          <h2 className="text-lg sm:text-xl font-bold text-slate-100">🎯 Qaysi maqsad bilan keldingiz?</h2>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">Sizga mos dars va yo'riqnomani darhol tanlang</p>
        </div>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {USER_GOALS.map((goal) => (
            <Link
              key={goal.slug}
              href={`/${goal.slug}`}
              className="group flex items-center gap-3 rounded-2xl border border-slate-800/80 bg-slate-900/60 p-4 font-semibold text-slate-200 transition-all duration-200 hover:-translate-y-1 hover:border-amber-500/60 hover:bg-slate-900 hover:shadow-lg hover:shadow-amber-500/10"
            >
              <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-slate-800/80 text-xl group-hover:scale-110 transition-transform">
                {goal.emoji}
              </span>
              <span className="text-sm group-hover:text-amber-400 transition-colors">{goal.label}</span>
            </Link>
          ))}
        </div>
      </section>

      <div className="grid gap-8 lg:grid-cols-[1fr_320px]">
        <div>
          {/* Bo'limlar */}
          {(categories || []).length > 0 && (
            <section className="mb-10">
              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-xl font-extrabold text-white flex items-center gap-2">
                  <span>📚</span> Yo'nalishlar Bo'yicha Darslar
                </h2>
              </div>
              <div className="grid gap-3 sm:grid-cols-2">
                {categories.map((cat) => (
                  <Link
                    key={cat.slug}
                    href={`/${cat.slug}`}
                    className="group flex items-center gap-3.5 rounded-2xl border border-slate-800/80 bg-slate-900/50 p-4 transition-all duration-200 hover:-translate-y-0.5 hover:border-amber-500/50 hover:bg-slate-900/90 hover:shadow-md"
                  >
                    <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-amber-500/10 border border-amber-500/20 text-2xl group-hover:scale-110 transition-transform">
                      {SECTION_ICONS[cat.slug] || "📘"}
                    </span>
                    <div>
                      <span className="block font-bold text-slate-200 group-hover:text-amber-400 transition-colors">
                        {cat.name}
                      </span>
                      <span className="text-xs text-slate-400">Barcha darslar →</span>
                    </div>
                  </Link>
                ))}
              </div>
            </section>
          )}

          {/* So'nggi darslar */}
          <section>
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-xl font-extrabold text-white flex items-center gap-2">
                <span>🆕</span> So'nggi Yangi Darslar
              </h2>
              <Link href="/biznesni-boshlash" className="text-xs font-semibold text-amber-400 hover:underline">
                Barchasini ko'rish →
              </Link>
            </div>

            {hasLessons ? (
              <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
                {latest.map((article) => (
                  <ArticleCard key={article.id} article={article} />
                ))}
              </div>
            ) : (
              <div className="rounded-2xl border border-slate-800 p-10 text-center leading-relaxed text-slate-400 bg-slate-900/40">
                Darslar yuklanmoqda...
              </div>
            )}
          </section>
        </div>

        <aside className="space-y-8">
          <section className="rounded-2xl border border-slate-800/80 bg-slate-900/40 p-5 backdrop-blur-sm">
            <h2 className="mb-3 font-bold text-slate-200 flex items-center gap-2 text-sm">
              <span>🔖</span> Ommabop Teglar
            </h2>
            <div className="flex flex-wrap gap-2">
              {(trends || []).length > 0 ? (
                trends.map((trend) => (
                  <Link
                    key={trend.teg}
                    href={`/qidiruv?q=${encodeURIComponent(trend.teg)}`}
                    className="rounded-xl border border-slate-800 bg-slate-900/80 px-3 py-1 text-xs text-slate-300 hover:border-amber-500/50 hover:bg-amber-500/10 hover:text-amber-400 transition-all"
                  >
                    #{trend.teg}
                  </Link>
                ))
              ) : (
                <p className="text-xs text-slate-500">Teglar yuklanmoqda...</p>
              )}
            </div>
          </section>
        </aside>
      </div>
    </div>
  );
}

import Link from "next/link";
import { apiGet } from "../lib/api";
import MobileNav from "./MobileNav";

export default async function Header() {
  const categories = (await apiGet("/api/categories")) || [];

  return (
    <>
      <header className="sticky top-0 z-40 border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md">
        <div className="mx-auto flex max-w-6xl flex-col gap-3 px-4 py-3 sm:py-4">
          <div className="flex items-center justify-between gap-3">
            <Link href="/" className="flex items-center gap-2 text-lg sm:text-xl font-bold shrink-0">
              <img src="/logo.svg" alt="Biznes Darslari logotipi" width={32} height={32} className="sm:w-9 sm:h-9" />
              <span>
                Biznes <span className="text-amber-400">Darslari</span>
              </span>
            </Link>

            <div className="hidden md:flex items-center gap-4">
              <a
                href="https://t.me/biznesxabari"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1.5 text-sm text-slate-300 hover:text-sky-400 transition-colors"
              >
                📢 Telegram Kanal
              </a>
              <a
                href="https://t.me/Biznesxabar_bot"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1.5 text-sm text-slate-300 hover:text-amber-400 transition-colors"
              >
                🤖 Telegram Bot
              </a>
              <form action="/qidiruv" className="relative w-72">
                <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-500">
                  🔍
                </span>
                <input
                  name="q"
                  placeholder="Darslardan qidiring..."
                  aria-label="Darslardan qidiruv"
                  className="w-full rounded-lg border border-slate-700 bg-slate-900 py-2 pl-9 pr-3 text-sm outline-none focus:border-amber-500"
                />
              </form>
            </div>

            {/* Mobile Header Quick Buttons */}
            <div className="flex md:hidden items-center gap-2">
              <Link
                href="/qidiruv"
                className="flex items-center justify-center rounded-lg border border-slate-800 bg-slate-900 p-2 text-slate-300"
                aria-label="Qidiruv"
              >
                🔍
              </Link>
              <a
                href="https://t.me/biznesxabari"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1 rounded-lg bg-sky-500/10 px-2.5 py-1.5 text-xs font-semibold text-sky-400 border border-sky-500/20"
              >
                📢 Telegram
              </a>
            </div>
          </div>

          {/* Category Navigation Pills (Scrolls on Mobile, Wraps Cleanly on Desktop) */}
          <nav className="flex overflow-x-auto md:flex-wrap gap-2 py-1 text-sm whitespace-nowrap md:whitespace-normal scrollbar-none">
            <Link
              href="/kalkulyator"
              className="inline-block rounded-full border border-amber-500/40 bg-amber-500/10 px-3.5 py-1 text-xs sm:text-sm font-semibold text-amber-400 hover:bg-amber-500 hover:text-slate-950 transition-all shrink-0"
            >
              🧮 Biznes Kalkulyatori
            </Link>
            <Link
              href="/hamkorlik"
              className="inline-block rounded-full border border-slate-800 bg-slate-900/60 px-3.5 py-1 text-xs sm:text-sm text-slate-300 hover:border-amber-500 hover:text-white transition-all shrink-0"
            >
              🤝 B2B Hamkorlik
            </Link>
            {categories.map((cat) => (
              <Link
                key={cat.slug}
                href={`/${cat.slug}`}
                className="inline-block rounded-full border border-slate-800 bg-slate-900/60 px-3.5 py-1 text-xs sm:text-sm text-slate-300 hover:border-amber-500 hover:text-white transition-all shrink-0"
              >
                {cat.name}
              </Link>
            ))}
          </nav>
        </div>
      </header>

      {/* Mobile Fixed Bottom Navigation Bar */}
      <MobileNav categories={categories} />
    </>
  );
}

import Link from "next/link";
import { apiGet } from "../lib/api";

export default async function Header() {
  const categories = (await apiGet("/api/categories")) || [];

  return (
    <header className="border-b border-slate-800">
      <div className="mx-auto flex max-w-6xl flex-col gap-3 px-4 py-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <Link href="/" className="flex items-center gap-2 text-xl font-bold">
            <img src="/logo.svg" alt="Biznes Darslari logotipi" width={36} height={36} />
            <span>
              Biznes <span className="text-amber-400">Darslari</span>
            </span>
          </Link>
          <div className="flex flex-wrap items-center gap-4">
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
            <form action="/qidiruv" className="relative w-full sm:w-72">
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
        </div>

        <nav className="flex flex-wrap gap-2 text-sm">
          {categories.map((cat) => (
            <Link
              key={cat.slug}
              href={`/kategoriya/${cat.slug}`}
              className="rounded-full border border-slate-700 px-3 py-1 text-slate-300 hover:border-amber-500 hover:text-white"
            >
              {cat.name}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}

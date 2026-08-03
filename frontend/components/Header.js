"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { apiGet } from "../lib/api";

export default function Header() {
  const [categories, setCategories] = useState([]);

  useEffect(() => {
    async function load() {
      const data = await apiGet("/api/categories");
      if (data && data.length > 0) {
        setCategories(data);
      }
    }
    load();
  }, []);

  return (
    <header className="sticky top-0 z-40 border-b border-slate-800 bg-slate-950/80 backdrop-blur-md">
      <div className="mx-auto max-w-6xl px-4 py-3">
        <div className="mb-2 flex items-center justify-between gap-4">
          <Link href="/" className="flex items-center gap-2">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src="/logo.svg" alt="Biznes Darslari Logo" className="h-9 w-9 rounded-lg shadow-sm" />
            <div>
              <span className="text-xl font-extrabold tracking-tight text-white">
                Biznes<span className="text-amber-400">Darslari</span>
              </span>
              <span className="hidden sm:inline-block ml-2 rounded-full bg-slate-800 px-2 py-0.5 text-[10px] font-semibold text-slate-300">
                .uz
              </span>
            </div>
          </Link>

          {/* Desktop Search Bar */}
          <div className="hidden md:flex flex-1 max-w-md items-center">
            <form action="/qidiruv" method="GET" className="relative w-full">
              <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400">
                🔍
              </span>
              <input
                name="q"
                placeholder="Darslardan qidiring..."
                aria-label="Darslardan qidiruv"
                className="w-full rounded-lg border border-slate-700 bg-slate-900 py-2 pl-9 pr-3 text-sm outline-none focus:border-amber-500 text-slate-100"
              />
            </form>
          </div>

          {/* Header Action Buttons */}
          <div className="flex items-center gap-2">
            <Link
              href="/qidiruv"
              className="flex md:hidden items-center justify-center rounded-lg border border-slate-800 bg-slate-900 p-2 text-slate-300"
              aria-label="Qidiruv"
            >
              🔍
            </Link>
            <a
              href="https://t.me/biznesxabari"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 rounded-lg bg-sky-500/10 px-3 py-1.5 text-xs font-semibold text-sky-400 border border-sky-500/20 hover:bg-sky-500/20 transition-all"
            >
              📢 Telegram
            </a>
          </div>
        </div>

        {/* 3 Main Product Pillars Navigation */}
        <nav className="flex overflow-x-auto md:flex-wrap gap-2 py-1 text-sm whitespace-nowrap md:whitespace-normal scrollbar-none items-center">
          <Link
            href="/biznes-goyalari"
            className="inline-block rounded-full border border-amber-500/50 bg-amber-500/10 px-3.5 py-1 text-xs sm:text-sm font-bold text-amber-400 hover:bg-amber-500 hover:text-slate-950 transition-all shrink-0"
          >
            💡 1. Biznes Toping (75+ G&apos;oya)
          </Link>
          <Link
            href="/biznesni-boshlash"
            className="inline-block rounded-full border border-slate-700 bg-slate-900 px-3.5 py-1 text-xs sm:text-sm font-bold text-slate-200 hover:border-amber-500 transition-all shrink-0"
          >
            🎓 2. O&apos;rganing (40+ Dars)
          </Link>
          <Link
            href="/kalkulyator"
            className="inline-block rounded-full border border-slate-700 bg-slate-900 px-3.5 py-1 text-xs sm:text-sm font-bold text-slate-200 hover:border-amber-500 transition-all shrink-0"
          >
            🧮 3. Ishlating (Kalkulyator)
          </Link>
          <Link
            href="/hamkorlik"
            className="inline-block rounded-full border border-slate-800 bg-slate-950 px-3.5 py-1 text-xs sm:text-sm text-slate-400 hover:text-slate-200 hover:border-slate-700 transition-all shrink-0"
          >
            🤝 B2B Hamkorlik
          </Link>

          <span className="hidden md:inline-block text-slate-700">|</span>

          {categories.map((cat) => (
            <Link
              key={cat.slug}
              href={`/${cat.slug}`}
              className="inline-block rounded-full border border-slate-800/80 bg-slate-900/40 px-3 py-1 text-xs text-slate-300 hover:border-amber-500/50 hover:text-white transition-all shrink-0"
            >
              {cat.name}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}

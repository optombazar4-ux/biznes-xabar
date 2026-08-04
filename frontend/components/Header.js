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
    <header className="sticky top-0 z-40 border-b border-slate-800/80 bg-slate-950/85 backdrop-blur-xl transition-all">
      <div className="mx-auto max-w-6xl px-4 py-2.5">
        <div className="mb-2 flex items-center justify-between gap-4">
          <Link href="/" className="group flex items-center gap-2.5">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="/logo.svg"
              alt="Biznes Darslari Logo"
              className="h-9 w-9 rounded-xl shadow-md transition-transform duration-300 group-hover:scale-105"
            />
            <div>
              <span className="text-xl font-black tracking-tight text-white">
                Biznes<span className="text-amber-400">Darslari</span>
              </span>
              <span className="hidden sm:inline-block ml-1.5 rounded-md bg-amber-500/10 border border-amber-500/20 px-1.5 py-0.5 text-[10px] font-bold text-amber-400">
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
                placeholder="113+ biznes darslaridan qidiring..."
                aria-label="Darslardan qidiruv"
                className="w-full rounded-xl border border-slate-800 bg-slate-900/80 py-2 pl-9 pr-3 text-xs sm:text-sm text-slate-100 placeholder-slate-400 outline-none transition-all focus:border-amber-500/80 focus:bg-slate-900 focus:ring-2 focus:ring-amber-500/20"
              />
            </form>
          </div>

          {/* Header Action Buttons */}
          <div className="flex items-center gap-2">
            <Link
              href="/qidiruv"
              className="flex md:hidden items-center justify-center rounded-xl border border-slate-800 bg-slate-900/80 p-2 text-slate-300 hover:text-white"
              aria-label="Qidiruv"
            >
              🔍
            </Link>
            <a
              href="https://t.me/biznesxabari"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1.5 rounded-xl bg-sky-500/10 px-3.5 py-1.5 text-xs font-bold text-sky-400 border border-sky-500/25 hover:bg-sky-500/20 hover:border-sky-500/40 transition-all shadow-sm"
            >
              <span>📢</span>
              <span className="hidden sm:inline">Telegram Kanal</span>
              <span className="sm:hidden">Telegram</span>
            </a>
          </div>
        </div>

        {/* 3 Main Product Pillars Navigation */}
        <nav className="flex overflow-x-auto md:flex-wrap gap-2 py-1 text-xs whitespace-nowrap md:whitespace-normal scrollbar-none items-center">
          <Link
            href="/biznes-goyalari"
            className="inline-flex items-center gap-1 rounded-full border border-amber-500/60 bg-amber-500/15 px-3.5 py-1 font-extrabold text-amber-300 hover:bg-amber-500 hover:text-slate-950 transition-all shrink-0 shadow-sm"
          >
            💡 1. G&apos;oya Toping
          </Link>
          <Link
            href="/biznesni-boshlash"
            className="inline-flex items-center gap-1 rounded-full border border-slate-700/80 bg-slate-900/80 px-3.5 py-1 font-bold text-slate-200 hover:border-amber-500/70 hover:text-amber-300 transition-all shrink-0"
          >
            🎓 2. Darslar (40+)
          </Link>
          <Link
            href="/kalkulyator"
            className="inline-flex items-center gap-1 rounded-full border border-slate-700/80 bg-slate-900/80 px-3.5 py-1 font-bold text-slate-200 hover:border-amber-500/70 hover:text-amber-300 transition-all shrink-0"
          >
            🧮 3. Kalkulyator
          </Link>
          <Link
            href="/hamkorlik"
            className="inline-flex items-center gap-1 rounded-full border border-slate-800/80 bg-slate-950/60 px-3.5 py-1 font-medium text-slate-400 hover:text-slate-200 hover:border-slate-700 transition-all shrink-0"
          >
            🤝 B2B Hamkorlik
          </Link>

          <span className="hidden md:inline-block text-slate-800 font-light">|</span>

          {categories.map((cat) => (
            <Link
              key={cat.slug}
              href={`/${cat.slug}`}
              className="inline-block rounded-full border border-slate-800/60 bg-slate-900/30 px-3 py-1 text-slate-300 hover:border-amber-500/50 hover:text-white transition-all shrink-0"
            >
              {cat.name}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}

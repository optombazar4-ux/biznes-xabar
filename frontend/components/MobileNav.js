"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { apiGet } from "../lib/api";

export default function MobileNav() {
  const pathname = usePathname();
  const [categories, setCategories] = useState([]);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    async function load() {
      const data = await apiGet("/api/categories");
      if (data && data.length > 0) setCategories(data);
    }
    load();
  }, []);

  const isCurrent = (path) => pathname === path;

  return (
    <>
      {/* Pastki Navigatsiya Paneli (Faqat Mobil Ekranda `md:hidden`) */}
      <div className="fixed bottom-0 left-0 right-0 z-50 border-t border-slate-800/80 bg-slate-950/90 backdrop-blur-xl md:hidden shadow-2xl">
        <div className="flex items-center justify-around py-2.5 px-2 text-[11px]">
          <Link
            href="/"
            className={`relative flex flex-col items-center gap-1 transition-all duration-200 ${
              isCurrent("/") ? "text-amber-400 font-bold scale-105" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <span className="text-xl">🏠</span>
            <span>Bosh sahifa</span>
            {isCurrent("/") && (
              <span className="absolute -bottom-1 h-1 w-5 rounded-full bg-amber-400 shadow-sm shadow-amber-400/50" />
            )}
          </Link>

          <Link
            href="/biznes-goyalari"
            className={`relative flex flex-col items-center gap-1 transition-all duration-200 ${
              isCurrent("/biznes-goyalari") ? "text-amber-400 font-bold scale-105" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <span className="text-xl">💡</span>
            <span>G&apos;oyalar</span>
            {isCurrent("/biznes-goyalari") && (
              <span className="absolute -bottom-1 h-1 w-5 rounded-full bg-amber-400 shadow-sm shadow-amber-400/50" />
            )}
          </Link>

          <Link
            href="/biznesni-boshlash"
            className={`relative flex flex-col items-center gap-1 transition-all duration-200 ${
              isCurrent("/biznesni-boshlash") ? "text-amber-400 font-bold scale-105" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <span className="text-xl">🎓</span>
            <span>Darslar</span>
            {isCurrent("/biznesni-boshlash") && (
              <span className="absolute -bottom-1 h-1 w-5 rounded-full bg-amber-400 shadow-sm shadow-amber-400/50" />
            )}
          </Link>

          <Link
            href="/kalkulyator"
            className={`relative flex flex-col items-center gap-1 transition-all duration-200 ${
              isCurrent("/kalkulyator") ? "text-amber-400 font-bold scale-105" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <span className="text-xl">🧮</span>
            <span>Kalkulyator</span>
            {isCurrent("/kalkulyator") && (
              <span className="absolute -bottom-1 h-1 w-5 rounded-full bg-amber-400 shadow-sm shadow-amber-400/50" />
            )}
          </Link>

          <button
            onClick={() => setMenuOpen(true)}
            className="flex flex-col items-center gap-1 text-slate-400 hover:text-slate-200 transition-colors"
          >
            <span className="text-xl">📂</span>
            <span>Bo&apos;limlar</span>
          </button>
        </div>
      </div>

      {/* Slide-Up Category Drawer Modal */}
      {menuOpen && (
        <div className="fixed inset-0 z-50 flex flex-col justify-end bg-black/75 backdrop-blur-md md:hidden animate-fadeIn">
          <div className="rounded-t-3xl border-t border-slate-800 bg-slate-900/95 p-6 shadow-2xl space-y-4 max-h-[85vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
              <div className="flex items-center gap-2">
                <span className="text-xl">📚</span>
                <h3 className="font-bold text-slate-100 text-base">Barcha Yo&apos;nalishlar</h3>
              </div>
              <button
                onClick={() => setMenuOpen(false)}
                className="rounded-full bg-slate-800/80 p-2 text-slate-400 hover:text-white transition-colors"
                aria-label="Yopish"
              >
                ✕
              </button>
            </div>

            <div className="grid grid-cols-2 gap-2.5 text-sm pt-1">
              <Link
                href="/biznes-goyalari"
                onClick={() => setMenuOpen(false)}
                className="flex items-center justify-between rounded-xl border border-amber-500/40 bg-gradient-to-r from-amber-500/20 via-amber-500/10 to-transparent p-3.5 font-bold text-amber-300 col-span-2 shadow-sm"
              >
                <span>💡 Biznes Toping (75+ G&apos;oya)</span>
                <span className="text-xs text-amber-400">Ko&apos;rish →</span>
              </Link>
              <Link
                href="/kalkulyator"
                onClick={() => setMenuOpen(false)}
                className="rounded-xl border border-slate-800 bg-slate-950/70 p-3.5 font-semibold text-slate-200 col-span-2 hover:border-slate-700 transition-colors"
              >
                🧮 Biznes Kalkulyatori
              </Link>
              <Link
                href="/hamkorlik"
                onClick={() => setMenuOpen(false)}
                className="rounded-xl border border-slate-800 bg-slate-950/70 p-3.5 font-semibold text-slate-200 col-span-2 hover:border-slate-700 transition-colors"
              >
                🤝 B2B Hamkorlik (Media Kit)
              </Link>
              {categories.map((cat) => (
                <Link
                  key={cat.slug}
                  href={`/${cat.slug}`}
                  onClick={() => setMenuOpen(false)}
                  className="rounded-xl border border-slate-800/80 bg-slate-950/50 p-3 text-slate-300 hover:border-amber-500/60 hover:text-amber-400 transition-all text-xs font-medium"
                >
                  {cat.name}
                </Link>
              ))}
            </div>
          </div>
        </div>
      )}
    </>
  );
}

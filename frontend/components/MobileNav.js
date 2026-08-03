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
      <div className="fixed bottom-0 left-0 right-0 z-50 border-t border-slate-800/80 bg-slate-950/90 backdrop-blur-lg md:hidden">
        <div className="flex items-center justify-around py-2 text-xs">
          <Link
            href="/"
            className={`flex flex-col items-center gap-1 transition-colors ${
              isCurrent("/") ? "text-amber-400 font-bold" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <span className="text-lg">🏠</span>
            <span>Bosh sahifa</span>
          </Link>

          <Link
            href="/biznes-goyalari"
            className={`flex flex-col items-center gap-1 transition-colors ${
              isCurrent("/biznes-goyalari") ? "text-amber-400 font-bold" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <span className="text-lg">💡</span>
            <span>G&apos;oyalar</span>
          </Link>

          <Link
            href="/biznesni-boshlash"
            className={`flex flex-col items-center gap-1 transition-colors ${
              isCurrent("/biznesni-boshlash") ? "text-amber-400 font-bold" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <span className="text-lg">🎓</span>
            <span>Darslar</span>
          </Link>

          <Link
            href="/kalkulyator"
            className={`flex flex-col items-center gap-1 transition-colors ${
              isCurrent("/kalkulyator") ? "text-amber-400 font-bold" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <span className="text-lg">🧮</span>
            <span>Kalkulyator</span>
          </Link>

          <button
            onClick={() => setMenuOpen(true)}
            className="flex flex-col items-center gap-1 text-slate-400 hover:text-slate-200 transition-colors"
          >
            <span className="text-lg">📂</span>
            <span>Bo&apos;limlar</span>
          </button>
        </div>
      </div>

      {/* Slide-Up Category Drawer Modal */}
      {menuOpen && (
        <div className="fixed inset-0 z-50 flex flex-col justify-end bg-black/70 backdrop-blur-sm md:hidden">
          <div className="rounded-t-2xl border-t border-slate-800 bg-slate-900 p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="font-bold text-slate-100 text-base">📚 Barcha Yo&apos;nalishlar</h3>
              <button
                onClick={() => setMenuOpen(false)}
                className="rounded-full bg-slate-800 p-1.5 text-slate-400 hover:text-white"
              >
                ✕
              </button>
            </div>

            <div className="grid grid-cols-2 gap-2 text-sm">
              <Link
                href="/biznes-goyalari"
                onClick={() => setMenuOpen(false)}
                className="rounded-xl border border-amber-500/30 bg-amber-500/10 p-3 font-bold text-amber-400 col-span-2"
              >
                💡 Biznes Toping (75+ G&apos;oya)
              </Link>
              <Link
                href="/kalkulyator"
                onClick={() => setMenuOpen(false)}
                className="rounded-xl border border-slate-800 bg-slate-950 p-3 font-semibold text-slate-200 col-span-2"
              >
                🧮 Biznes Kalkulyatori
              </Link>
              <Link
                href="/hamkorlik"
                onClick={() => setMenuOpen(false)}
                className="rounded-xl border border-slate-800 bg-slate-950 p-3 font-semibold text-slate-200 col-span-2"
              >
                🤝 B2B Hamkorlik (Media Kit)
              </Link>
              {categories.map((cat) => (
                <Link
                  key={cat.slug}
                  href={`/${cat.slug}`}
                  onClick={() => setMenuOpen(false)}
                  className="rounded-xl border border-slate-800 bg-slate-950/60 p-3 text-slate-300 hover:border-amber-500"
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

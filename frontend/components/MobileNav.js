"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

export default function MobileNav({ categories = [] }) {
  const [menuOpen, setMenuOpen] = useState(false);
  const pathname = usePathname();

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

          <Link
            href="/qidiruv"
            className={`flex flex-col items-center gap-1 transition-colors ${
              isCurrent("/qidiruv") ? "text-amber-400 font-bold" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <span className="text-lg">🔍</span>
            <span>Qidiruv</span>
          </Link>
        </div>
      </div>

      {/* Bo'limlar Drawer Modali (Slide-Up Modal) */}
      {menuOpen && (
        <div className="fixed inset-0 z-50 flex flex-col justify-end bg-black/70 backdrop-blur-sm md:hidden">
          <div className="max-h-[80vh] w-full overflow-y-auto rounded-t-2xl border-t border-slate-800 bg-slate-900 p-6 shadow-2xl">
            <div className="mb-4 flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-lg font-bold text-slate-100">📂 Bo&apos;limlar Katalogi</h3>
              <button
                onClick={() => setMenuOpen(false)}
                className="rounded-full bg-slate-800 p-2 text-slate-400 hover:text-white"
              >
                ✕
              </button>
            </div>

            <div className="grid grid-cols-2 gap-3">
              {categories.map((cat) => (
                <Link
                  key={cat.slug}
                  href={`/${cat.slug}`}
                  onClick={() => setMenuOpen(false)}
                  className={`flex flex-col rounded-xl border p-3.5 transition-all ${
                    isCurrent(`/${cat.slug}`)
                      ? "border-amber-500 bg-amber-500/10 text-amber-400 font-bold"
                      : "border-slate-800 bg-slate-950/60 text-slate-300 hover:border-slate-700"
                  }`}
                >
                  <span className="text-sm font-semibold">{cat.name}</span>
                </Link>
              ))}
            </div>

            <div className="mt-6 border-t border-slate-800 pt-4 text-center">
              <a
                href="https://t.me/biznesxabari"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center gap-2 rounded-xl bg-sky-500/10 px-4 py-2.5 text-sm font-semibold text-sky-400 border border-sky-500/20 w-full"
              >
                📢 Telegram Kanalimizga A&apos;zo Bo&apos;ling
              </a>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

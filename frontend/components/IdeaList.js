"use client";

import Link from "next/link";
import { useMemo, useState } from "react";

const FILTERS = [
  { value: "barchasi", label: "Barchasi" },
  { value: "5 mln gacha", label: "5 mln gacha" },
  { value: "uydan", label: "Uydan" },
  { value: "onlayn", label: "Onlayn" },
  { value: "qishloq", label: "Qishloq" },
  { value: "xizmat", label: "Xizmat" },
  { value: "savdo", label: "Savdo" },
  { value: "ishlab chiqarish", label: "Ishlab chiqarish" },
];

export default function IdeaList({ ideas }) {
  const [activeFilter, setActiveFilter] = useState("barchasi");
  const visibleIdeas = useMemo(
    () =>
      activeFilter === "barchasi"
        ? ideas
        : ideas.filter((idea) => (idea.tags || []).includes(activeFilter)),
    [activeFilter, ideas],
  );

  return (
    <div>
      <div className="mb-6 flex flex-wrap gap-2" aria-label="Biznes g'oyalarini filtrlash">
        {FILTERS.map((filter) => (
          <button
            key={filter.value}
            type="button"
            onClick={() => setActiveFilter(filter.value)}
            className={`rounded-full border px-3 py-1.5 text-sm transition ${
              activeFilter === filter.value
                ? "border-amber-500 bg-amber-500 font-semibold text-slate-950"
                : "border-slate-700 bg-slate-900 text-slate-300 hover:border-amber-500"
            }`}
          >
            {filter.label}
          </button>
        ))}
      </div>

      <p className="mb-4 text-sm text-slate-400">
        {visibleIdeas.length} ta verifikatsiya qilingan g&apos;oya
      </p>

      {visibleIdeas.length > 0 ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {visibleIdeas.map((idea) => (
            <article
              key={idea.slug}
              className="flex flex-col rounded-xl border border-slate-800 bg-slate-900/60 p-5 transition hover:border-amber-600 backdrop-blur-md"
            >
              <div className="mb-3 flex flex-wrap items-center justify-between gap-1.5">
                <div className="flex flex-wrap gap-1.5">
                  {(idea.tags || [])
                    .filter((tag) => FILTERS.some((filter) => filter.value === tag))
                    .map((tag) => (
                      <span
                        key={tag}
                        className="rounded-full bg-amber-500/10 px-2.5 py-0.5 text-[11px] font-semibold text-amber-400 border border-amber-500/20"
                      >
                        {tag}
                      </span>
                    ))}
                </div>
                <span className="rounded-full bg-emerald-500/10 px-2 py-0.5 text-[10px] font-semibold text-emerald-400 border border-emerald-500/20">
                  🟢 Bozor Data Verifikatsiyasi
                </span>
              </div>
              <h2 className="mb-2 font-semibold leading-snug text-slate-100 text-base">{idea.title}</h2>
              <p className="mb-4 line-clamp-3 text-sm leading-relaxed text-slate-300">
                {idea.summary}
              </p>
              <div className="mt-auto flex items-center justify-between text-xs pt-3 border-t border-slate-800/60">
                <span className="text-slate-400">⏱ {idea.minutes} daqiqa o&apos;qish</span>
                <Link
                  href={`/biznes-goyalari/${idea.slug}`}
                  className="font-semibold text-amber-400 hover:underline flex items-center gap-1"
                >
                  G&apos;oyani ko&apos;rish →
                </Link>
              </div>
            </article>
          ))}
        </div>
      ) : (
        <div className="rounded-xl border border-slate-800 p-8 text-center text-slate-400">
          Bu filtr bo&apos;yicha g&apos;oya hali tayyorlanmagan.
        </div>
      )}
    </div>
  );
}

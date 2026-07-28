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
        {visibleIdeas.length} ta mos g&apos;oya
      </p>

      {visibleIdeas.length > 0 ? (
        <div className="grid gap-4 sm:grid-cols-2">
          {visibleIdeas.map((idea) => (
            <article
              key={idea.slug}
              className="flex flex-col rounded-xl border border-slate-800 bg-slate-900/60 p-5 transition hover:border-amber-600"
            >
              <div className="mb-3 flex flex-wrap gap-1.5">
                {(idea.tags || [])
                  .filter((tag) => FILTERS.some((filter) => filter.value === tag))
                  .map((tag) => (
                    <span
                      key={tag}
                      className="rounded-full bg-amber-500/10 px-2.5 py-1 text-[11px] font-semibold text-amber-400"
                    >
                      {tag}
                    </span>
                  ))}
              </div>
              <h2 className="mb-2 font-semibold leading-snug">{idea.title}</h2>
              <p className="mb-4 line-clamp-3 text-sm leading-relaxed text-slate-400">
                {idea.summary}
              </p>
              <div className="mt-auto flex items-center justify-between text-xs">
                <span className="text-slate-500">⏱ {idea.minutes} daqiqa</span>
                <Link
                  href={`/biznes-goyalari/${idea.slug}`}
                  className="font-semibold text-amber-400 hover:underline"
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

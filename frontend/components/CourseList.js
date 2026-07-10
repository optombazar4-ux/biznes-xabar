"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { getReadSlugs } from "../lib/progress";

// Bo'lim (kurs) darslarini ketma-ketlikda, progress va o'qilgan belgilari bilan ko'rsatadi.
export default function CourseList({ lessons, categorySlug }) {
  const [readSlugs, setReadSlugs] = useState([]);

  useEffect(() => {
    setReadSlugs(getReadSlugs());
  }, []);

  const readSet = new Set(readSlugs);
  const done = lessons.filter((l) => readSet.has(l.slug)).length;
  const pct = lessons.length ? Math.round((done / lessons.length) * 100) : 0;
  const nextIndex = lessons.findIndex((l) => !readSet.has(l.slug));

  return (
    <div>
      {/* Progress */}
      <div className="mb-6 rounded-xl border border-slate-800 bg-slate-900/60 p-4">
        <div className="mb-2 flex items-center justify-between text-sm">
          <span className="font-semibold text-slate-200">
            {done} / {lessons.length} dars o&apos;rganildi
          </span>
          <span className="text-amber-400">{pct}%</span>
        </div>
        <div className="h-2 w-full overflow-hidden rounded-full bg-slate-800">
          <div
            className="h-full rounded-full bg-amber-500 transition-all"
            style={{ width: `${pct}%` }}
          />
        </div>
      </div>

      {/* Darslar ketma-ketligi */}
      <ol className="space-y-3">
        {lessons.map((lesson, i) => {
          const isDone = readSet.has(lesson.slug);
          const isNext = i === nextIndex;
          return (
            <li key={lesson.slug}>
              <Link
                href={`/${categorySlug}/${lesson.slug}`}
                className={`flex items-start gap-3 rounded-xl border p-4 transition ${
                  isNext
                    ? "border-amber-500 bg-amber-500/5"
                    : "border-slate-800 bg-slate-900/60 hover:border-amber-600"
                }`}
              >
                <span
                  className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-sm font-bold ${
                    isDone
                      ? "bg-amber-500 text-slate-950"
                      : "bg-slate-800 text-slate-400"
                  }`}
                >
                  {isDone ? "✓" : i + 1}
                </span>
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="font-medium leading-snug">{lesson.title}</span>
                    {isNext && (
                      <span className="rounded-full bg-amber-500 px-2 py-0.5 text-[11px] font-bold text-slate-950">
                        Keyingi dars
                      </span>
                    )}
                  </div>
                  <div className="mt-1 text-xs text-slate-500">⏱ {lesson.minutes} daqiqa</div>
                </div>
              </Link>
            </li>
          );
        })}
      </ol>
    </div>
  );
}

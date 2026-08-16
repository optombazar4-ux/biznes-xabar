import Link from "next/link";
import { articleMinutes, levelForCategory, formatDate } from "../lib/lesson";

export default function ArticleCard({ article, compact = false }) {
  const category = article.category?.name || "Biznes darsi";
  const catSlug = article.category?.slug || "biznesni-boshlash";
  const href = `/${catSlug}/${article.slug}`;
  const level = levelForCategory(article.category?.slug);
  const minutes = articleMinutes(article);
  const date = formatDate(article.published_at);

  if (compact) {
    return (
      <Link
        href={href}
        className="group block rounded-xl border border-slate-800/80 bg-slate-900/40 p-3.5 transition-all duration-200 hover:border-amber-500/50 hover:bg-slate-900/80 hover:shadow-md hover:shadow-amber-500/5"
      >
        <div className="mb-1 text-[11px] font-medium text-amber-400/90">{category}</div>
        <div className="text-sm font-semibold leading-snug text-slate-200 group-hover:text-white transition-colors">
          {article.title}
        </div>
      </Link>
    );
  }

  return (
    <article className="group flex flex-col overflow-hidden rounded-2xl border border-slate-800/80 bg-slate-900/50 backdrop-blur-sm transition-all duration-300 hover:-translate-y-1 hover:border-amber-500/60 hover:shadow-xl hover:shadow-amber-500/10">
      <Link href={href} className="relative block h-44 overflow-hidden bg-slate-950">
        {article.image_url ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={article.image_url}
            alt=""
            className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center bg-gradient-to-br from-amber-950/70 via-slate-900 to-slate-950 text-5xl transition-transform duration-500 group-hover:scale-105">
            🎓
          </div>
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-slate-950/80 via-transparent to-transparent opacity-60 group-hover:opacity-40 transition-opacity" />
        <div className="absolute top-3 left-3 flex items-center gap-1.5">
          <span className="rounded-full border border-amber-500/30 bg-slate-950/80 px-2.5 py-0.5 text-[11px] font-bold text-amber-400 backdrop-blur-md shadow-sm">
            {category}
          </span>
        </div>
      </Link>
      <div className="flex flex-1 flex-col p-5">
        <div className="mb-2 flex items-center gap-2 text-xs text-slate-400">
          <span className="rounded-md bg-slate-800/80 px-2 py-0.5 text-[10px] font-medium text-slate-300">
            {level}
          </span>
          <span>•</span>
          <span>⏱ {minutes} min o&apos;qish</span>
        </div>
        <Link href={href} className="group/title">
          <h2 className="mb-2 text-base font-bold leading-snug text-slate-100 group-hover/title:text-amber-400 transition-colors line-clamp-2">
            {article.title}
          </h2>
        </Link>
        <p className="mb-4 line-clamp-2 text-xs leading-relaxed text-slate-400">
          {article.summary}
        </p>
        <div className="mt-auto flex items-center justify-between border-t border-slate-800/60 pt-3 text-xs text-slate-400">
          <span>{date || "Amaliy dars"}</span>
          <Link
            href={href}
            className="flex items-center gap-1 font-semibold text-amber-400 group-hover:translate-x-1 transition-transform"
          >
            Darsni o&apos;qish <span className="text-sm">→</span>
          </Link>
        </div>
      </div>
    </article>
  );
}

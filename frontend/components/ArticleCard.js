import Link from "next/link";
import { readingMinutes, levelForCategory, formatDate } from "../lib/lesson";

export default function ArticleCard({ article, compact = false }) {
  const category = article.category?.name || "Biznes darsi";
  const level = levelForCategory(article.category?.slug);
  const minutes = readingMinutes(article.content);
  const date = formatDate(article.published_at);

  if (compact) {
    return (
      <Link
        href={`/maqola/${article.slug}`}
        className="block rounded-lg border border-slate-800 p-3 hover:border-amber-600"
      >
        <div className="mb-1 text-xs text-slate-400">{category}</div>
        <div className="text-sm font-medium leading-snug">{article.title}</div>
      </Link>
    );
  }

  return (
    <article className="flex flex-col overflow-hidden rounded-xl border border-slate-800 bg-slate-900/60 transition hover:border-amber-600">
      {article.image_url ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img src={article.image_url} alt="" className="h-40 w-full object-cover" />
      ) : (
        <div className="flex h-40 w-full items-center justify-center bg-gradient-to-br from-amber-950 to-slate-900 text-5xl">
          🎓
        </div>
      )}
      <div className="flex flex-1 flex-col p-5">
        <div className="mb-2 flex flex-wrap items-center gap-2 text-xs">
          <span className="rounded-full bg-amber-500/10 px-2.5 py-0.5 font-semibold text-amber-400">
            {category}
          </span>
          <span className="text-slate-500">{level}</span>
        </div>
        <Link href={`/maqola/${article.slug}`}>
          <h2 className="mb-2 text-lg font-semibold leading-snug hover:text-amber-400">
            {article.title}
          </h2>
        </Link>
        <p className="mb-4 line-clamp-2 text-sm leading-relaxed text-slate-400">
          {article.summary}
        </p>
        <div className="mt-auto flex items-center justify-between text-xs text-slate-500">
          <span>⏱ {minutes} daqiqa{date ? ` · ${date}` : ""}</span>
          <Link href={`/maqola/${article.slug}`} className="font-medium text-amber-400 hover:underline">
            O&apos;qish →
          </Link>
        </div>
      </div>
    </article>
  );
}

import { permanentRedirect, notFound } from "next/navigation";
import { apiGet } from "../../../lib/api";

// Eski manzil (/maqola/{slug}) -> yangi toza manzil (/{kategoriya}/{slug}) 301 redirect.
export default async function LegacyLessonRedirect({ params }) {
  const { slug } = await params;
  const article = await apiGet(`/api/news/${slug}`);
  if (!article) notFound();
  const catSlug = article.category?.slug || "biznesni-boshlash";
  permanentRedirect(`/${catSlug}/${slug}`);
}

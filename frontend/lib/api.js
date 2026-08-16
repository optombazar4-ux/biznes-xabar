import fallbackData from "./fallback-data.json";

const isServer = typeof window === "undefined";
const API_URL =
  (isServer && process.env.API_URL_INTERNAL) ||
  process.env.NEXT_PUBLIC_API_URL ||
  "http://localhost:8000";

function filterFallbackNews(params = {}) {
  let list = fallbackData.articles || [];
  
  if (params.kategoriya) {
    list = list.filter((a) => a.category?.slug === params.kategoriya);
  }
  
  if (params.q) {
    const q = params.q.toLowerCase();
    list = list.filter(
      (a) =>
        a.title.toLowerCase().includes(q) ||
        a.summary.toLowerCase().includes(q) ||
        (a.tags && a.tags.some((t) => t.toLowerCase().includes(q)))
    );
  }

  if (params.limit) {
    list = list.slice(0, Number(params.limit));
  }

  return list;
}

function getFallbackArticle(slug) {
  return (fallbackData.articles || []).find((a) => a.slug === slug) || null;
}

function getFallbackRelated(slug) {
  const current = getFallbackArticle(slug);
  if (!current) return [];
  const catSlug = current.category?.slug;
  return (fallbackData.articles || [])
    .filter((a) => a.slug !== slug && a.category?.slug === catSlug)
    .slice(0, 4);
}

// Ilgari har bir so'rov `cache: "no-store"` bilan ketardi, ya'ni har bir
// tashrifchi uchun baza qaytadan o'qilardi. Pipeline soatiga bir nechta dars
// qo'shadi, shuning uchun 5 daqiqalik kesh kontentni sezilarli eskirtirmaydi,
// lekin baza trafigini keskin kamaytiradi.
const DEFAULT_REVALIDATE = 300;

export async function apiGet(path, params = {}, { revalidate = DEFAULT_REVALIDATE } = {}) {
  const url = new URL(`${API_URL}${path}`);
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) url.searchParams.set(key, value);
  });

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 4000);

    const res = await fetch(url, {
      next: { revalidate },
      signal: controller.signal,
    });
    clearTimeout(timeoutId);

    if (!res.ok) throw new Error(`API ${res.status}`);
    return await res.json();
  } catch (err) {
    // API server yo'q bo'lsa yoki offline bo'lsa fallback ishlashiga o'tamiz
  }

  // Fallback ma'lumotlar bilan ta'minlash (offline / build vaqtida ham 100% ishlaydi)
  if (path === "/api/news" || path.startsWith("/api/news?")) {
    return filterFallbackNews(params);
  }
  if (path === "/api/categories") {
    return fallbackData.categories || [];
  }
  if (path === "/api/news/stats") {
    const list = fallbackData.articles || [];
    return {
      jami_darslar: list.length,
      biznes_goyalar: list.filter(
        (a) => a.category?.slug === "biznes-goyalari"
      ).length,
    };
  }
  if (path === "/api/news/trends") {
    const counts = new Map();
    for (const article of fallbackData.articles || []) {
      for (const tag of article.tags || []) {
        counts.set(tag, (counts.get(tag) || 0) + 1);
      }
    }
    return [...counts.entries()]
      .sort((a, b) => b[1] - a[1])
      .slice(0, Number(params.limit) || 15)
      .map(([teg, soni]) => ({ teg, soni }));
  }
  if (path === "/api/news/sitemap") {
    return (fallbackData.articles || []).map((article) => ({
      slug: article.slug,
      category_slug: article.category?.slug || "biznesni-boshlash",
      tags: article.tags || [],
      published_at: article.published_at || null,
      created_at: article.created_at,
    }));
  }
  if (path.startsWith("/api/news/") && path.endsWith("/related")) {
    const parts = path.split("/");
    const slug = parts[3];
    return getFallbackRelated(slug);
  }
  if (path.startsWith("/api/news/")) {
    const slug = path.replace("/api/news/", "");
    return getFallbackArticle(slug);
  }

  return null;
}

export async function apiPost(path, body = {}) {
  const url = `${API_URL}${path}`;
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || `API ${res.status}`);
  }
  return await res.json();
}

export { API_URL };

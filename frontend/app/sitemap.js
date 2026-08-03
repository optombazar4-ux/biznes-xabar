import { apiGet } from "../lib/api";
import { SITE_URL } from "../lib/site";

const INTENTS = [
  "5-mln-gacha",
  "uydan",
  "qishloq",
  "onlayn",
  "xizmat",
  "savdo",
  "ishlab-chiqarish",
];

export default async function sitemap() {
  const articles = (await apiGet("/api/news", { limit: 1000 })) || [];
  const categories = (await apiGet("/api/categories")) || [];

  const articleUrls = articles.map((article) => {
    const catSlug = article.category?.slug || "biznesni-boshlash";
    return {
      url: `${SITE_URL}/${catSlug}/${article.slug}`,
      lastModified: article.published_at ? new Date(article.published_at) : new Date(),
      changeFrequency: "weekly",
      priority: 0.7,
    };
  });

  const categoryUrls = categories.map((cat) => ({
    url: `${SITE_URL}/${cat.slug}`,
    lastModified: new Date(),
    changeFrequency: "daily",
    priority: 0.8,
  }));

  const intentUrls = INTENTS.map((intent) => ({
    url: `${SITE_URL}/biznes-goyalari/${intent}`,
    lastModified: new Date(),
    changeFrequency: "daily",
    priority: 0.9,
  }));

  const staticUrls = ["/haqida", "/aloqa", "/maxfiylik"].map((path) => ({
    url: `${SITE_URL}${path}`,
    lastModified: new Date(),
    changeFrequency: "monthly",
    priority: 0.4,
  }));

  return [
    {
      url: SITE_URL,
      lastModified: new Date(),
      changeFrequency: "always",
      priority: 1.0,
    },
    ...categoryUrls,
    ...intentUrls,
    ...staticUrls,
    ...articleUrls,
  ];
}

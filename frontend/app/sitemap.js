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

const INTENT_TAGS = {
  "5-mln-gacha": "5 mln gacha",
  uydan: "uydan",
  qishloq: "qishloq",
  onlayn: "onlayn",
  xizmat: "xizmat",
  savdo: "savdo",
  "ishlab-chiqarish": "ishlab chiqarish",
};

function articleDate(article) {
  const value = article.published_at || article.created_at;
  if (!value) return null;
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? null : date;
}

function latestDate(articles) {
  return articles.reduce((latest, article) => {
    const date = articleDate(article);
    return date && (!latest || date > latest) ? date : latest;
  }, null);
}

export default async function sitemap() {
  const articles = (await apiGet("/api/news/sitemap")) || [];
  const categories = (await apiGet("/api/categories")) || [];
  const newestArticleDate = latestDate(articles);

  const articleUrls = articles.map((article) => {
    const lastModified = articleDate(article);
    const entry = {
      url: `${SITE_URL}/${article.category_slug}/${article.slug}`,
      changeFrequency: "weekly",
      priority: 0.7,
    };
    if (lastModified) entry.lastModified = lastModified;
    return entry;
  });

  const categoryUrls = categories.map((cat) => {
    const lastModified = latestDate(
      articles.filter((article) => article.category_slug === cat.slug),
    );
    return {
      url: `${SITE_URL}/${cat.slug}`,
      ...(lastModified ? { lastModified } : {}),
      changeFrequency: "daily",
      priority: 0.8,
    };
  });

  const intentUrls = INTENTS.map((intent) => {
    const expectedTag = INTENT_TAGS[intent];
    const lastModified = latestDate(
      articles.filter((article) => (article.tags || []).includes(expectedTag)),
    );
    return {
      url: `${SITE_URL}/biznes-goyalari/${intent}`,
      ...(lastModified ? { lastModified } : {}),
      changeFrequency: "daily",
      priority: 0.9,
    };
  });

  const staticUrls = ["/kalkulyator", "/hamkorlik", "/haqida", "/aloqa", "/maxfiylik"].map((path) => ({
    url: `${SITE_URL}${path}`,
    changeFrequency: "monthly",
    priority: 0.4,
  }));

  return [
    {
      url: SITE_URL,
      ...(newestArticleDate ? { lastModified: newestArticleDate } : {}),
      changeFrequency: "daily",
      priority: 1.0,
    },
    ...categoryUrls,
    ...intentUrls,
    ...staticUrls,
    ...articleUrls,
  ];
}

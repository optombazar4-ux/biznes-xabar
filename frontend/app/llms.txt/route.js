import { apiGet } from "../../lib/api";
import { SITE_NAME, SITE_URL } from "../../lib/site";

export const revalidate = 3600;

export async function GET() {
  const articles = (await apiGet("/api/news", { limit: 20 })) || [];

  const lines = [
    `# ${SITE_NAME}`,
    "",
    "> O'zbekistonda biznes ochish va yuritish bo'yicha bepul amaliy darslar, biznes g'oyalari, soliq yo'riqnomalari va moliyaviy kalkulyatorlar platformasi.",
    "",
    "## Asosiy bo'limlar",
    `- [Biznes g'oyalari](${SITE_URL}/biznes-goyalari): O'zbekiston bozoriga mos amaliy biznes g'oyalari`,
    `- [5 mln so'mgacha biznes g'oyalari](${SITE_URL}/biznes-goyalari/5-mln-gacha): Kam sarmoya bilan boshlanadigan loyihalar`,
    `- [Biznesni boshlash](${SITE_URL}/biznesni-boshlash): YaTT, MChJ va noldan biznes ochish`,
    `- [Moliya va hisob](${SITE_URL}/moliya): Tannarx, soliqlar va pul oqimi`,
    `- [Marketing va sotuv](${SITE_URL}/marketing-sotuv): Mijoz jalb qilish va sotuv voronkasi`,
    `- [Boshqaruv va o'sish](${SITE_URL}/boshqaruv): KPI, jamoa va jarayonlar`,
    `- [Onlayn biznes](${SITE_URL}/onlayn-biznes): Uzum Market, Payme, Click va Telegram`,
    `- [Amaliy ko'nikmalar](${SITE_URL}/amaliy-konikmalar): Muzokara, risk va shartnomalar`,
    `- [Biznes kalkulyatori](${SITE_URL}/kalkulyator): Marja, tannarx va break-even hisoblagich`,
    `- [Sitemap](${SITE_URL}/sitemap.xml)`,
    `- [RSS Feed](${SITE_URL}/api/news/rss)`,
    "",
    "## So'nggi darslar va biznes g'oyalari",
  ];

  for (const article of articles) {
    const catSlug = article.category?.slug || "biznesni-boshlash";
    const url = `${SITE_URL}/${catSlug}/${article.slug}`;
    const summary = String(article.summary || "")
      .replace(/\s+/g, " ")
      .trim()
      .slice(0, 160);
    lines.push(summary ? `- [${article.title}](${url}): ${summary}` : `- [${article.title}](${url})`);
  }

  return new Response(`${lines.join("\n")}\n`, {
    headers: {
      "Content-Type": "text/plain; charset=utf-8",
      "Cache-Control": "public, s-maxage=3600, stale-while-revalidate=86400",
    },
  });
}

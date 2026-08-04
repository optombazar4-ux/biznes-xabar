// Saytning tashqi (kanonik) manzili — SEO, sitemap, OG teglar uchun.

// SITE_URL har doim kanonik bo'lishi shart: https + www'siz + trailing slash'siz.
// Aks holda sitemap/OG URL'lari Search Console'da "URL not allowed for Sitemap
// in this location" xatolariga olib kelishi mumkin.
function normalizeSiteUrl(value) {
  return String(value || "https://biznesdarslari.uz")
    .trim()
    .replace(/\/+$/, "") // oxirgi slash'larni olib tashlaymiz
    .replace(/^https?:\/\/www\./, "https://"); // www -> canonical (non-www)
}

export const SITE_URL = normalizeSiteUrl(process.env.NEXT_PUBLIC_SITE_URL);


export const SITE_NAME = "Biznes Darslari";
export const SITE_ALT_NAMES = ["Biznes Maktab", "Tadbirkorlik Darslari"];
export const TELEGRAM_CHANNEL_URL = process.env.NEXT_PUBLIC_TELEGRAM_CHANNEL_URL || "https://t.me/biznesxabari";

// O'qilgan darslarni brauzer xotirasida (localStorage) saqlaydi —
// akkaunt talab qilmaydi. Faqat klient komponentlarida ishlatiladi.

const KEY = "bd_read_lessons";

export function getReadSlugs() {
  if (typeof window === "undefined") return [];
  try {
    return JSON.parse(localStorage.getItem(KEY) || "[]");
  } catch {
    return [];
  }
}

export function markRead(slug) {
  if (typeof window === "undefined" || !slug) return;
  const slugs = new Set(getReadSlugs());
  slugs.add(slug);
  localStorage.setItem(KEY, JSON.stringify([...slugs]));
}

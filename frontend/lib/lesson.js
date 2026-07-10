// Dars kartalari va sahifalari uchun yordamchi funksiyalar.

// Matndan taxminiy o'qish vaqtini (daqiqa) hisoblaydi — o'zbek tili uchun ~160 so'z/daqiqa.
export function readingMinutes(content) {
  const words = (content || "").trim().split(/\s+/).filter(Boolean).length;
  return Math.max(1, Math.round(words / 160));
}

// Bo'lim (kategoriya) bo'yicha darajani belgilaydi.
const LEVEL_BY_CATEGORY = {
  "biznesni-boshlash": "Boshlang'ich",
  moliya: "Boshlang'ich",
  "marketing-sotuv": "O'rta",
  boshqaruv: "O'rta",
  "onlayn-biznes": "O'rta",
  "amaliy-konikmalar": "Yuqori",
};

export function levelForCategory(slug) {
  return LEVEL_BY_CATEGORY[slug] || "Boshlang'ich";
}

// Sanani qisqa o'zbekcha formatda ko'rsatadi.
export function formatDate(value) {
  if (!value) return "";
  try {
    return new Date(value).toLocaleDateString("uz-UZ", {
      day: "numeric",
      month: "long",
      year: "numeric",
    });
  } catch {
    return "";
  }
}

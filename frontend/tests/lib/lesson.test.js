import { describe, it, expect } from "vitest";
import {
  readingMinutes,
  levelForCategory,
  formatDate,
} from "../../lib/lesson";

describe("readingMinutes", () => {
  it("bo'sh yoki null matn uchun kamida 1 daqiqa qaytaradi", () => {
    expect(readingMinutes("")).toBe(1);
    expect(readingMinutes(null)).toBe(1);
    expect(readingMinutes(undefined)).toBe(1);
  });

  it("~160 so'z/daqiqa tezligida to'g'ri yaxlitlaydi", () => {
    const oneMinute = Array(160).fill("so'z").join(" ");
    expect(readingMinutes(oneMinute)).toBe(1);

    const twoMinutes = Array(320).fill("so'z").join(" ");
    expect(readingMinutes(twoMinutes)).toBe(2);
  });

  it("bo'sh joylarni ortiqcha sanamaydi", () => {
    expect(readingMinutes("   bir   ikki  ")).toBe(1);
  });
});

describe("levelForCategory", () => {
  it("ma'lum kategoriyalarni to'g'ri xaritaga oladi", () => {
    expect(levelForCategory("biznes-goyalari")).toBe("G'oya");
    expect(levelForCategory("biznesni-boshlash")).toBe("Boshlang'ich");
    expect(levelForCategory("moliya")).toBe("Boshlang'ich");
    expect(levelForCategory("marketing-sotuv")).toBe("O'rta");
    expect(levelForCategory("boshqaruv")).toBe("O'rta");
    expect(levelForCategory("onlayn-biznes")).toBe("O'rta");
    expect(levelForCategory("amaliy-konikmalar")).toBe("Yuqori");
  });

  it("noma'lum kategoriya uchun standart qiymat qaytaradi", () => {
    expect(levelForCategory("nomalum")).toBe("Boshlang'ich");
    expect(levelForCategory(null)).toBe("Boshlang'ich");
  });
});

describe("formatDate", () => {
  it("yolg'on (falsy) qiymatlar uchun bo'sh qaytaradi", () => {
    expect(formatDate(null)).toBe("");
    expect(formatDate("")).toBe("");
    expect(formatDate(undefined)).toBe("");
  });

  it("haqiqiy sanani o'zbekcha formatda chiqaradi", () => {
    const out = formatDate("2026-08-04T00:00:00Z");
    expect(out).toContain("2026");
    expect(out.length).toBeGreaterThan(3);
  });
});

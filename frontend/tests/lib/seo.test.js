import { describe, it, expect } from "vitest";
import {
  fitMetaDescription,
  fitMetaTitle,
  plainMetaTitle,
  truncateWords,
} from "../../lib/seo";
import { SITE_NAME } from "../../lib/site";

function renderedTitleLength(titleValue) {
  if (typeof titleValue === "string") {
    return `${titleValue} — ${SITE_NAME}`.length;
  }
  return titleValue.absolute.length;
}

describe("truncateWords", () => {
  it("qisqa matnni o'zgarishsiz qaytaradi", () => {
    expect(truncateWords("  Salom   dunyo  ", 25)).toBe("Salom dunyo");
  });

  it("uzun matnni so'z chegarasida qirqib maksimal uzunlikda saqlaydi", () => {
    const text =
      "O'zbekistonda kichik biznes boshlash uchun amaliy qo'llanma va boshlang'ich sarmoya hisob-kitoblari";
    const out = truncateWords(text, 55);
    expect(out.length).toBeLessThanOrEqual(55);
    expect(out.endsWith("…")).toBe(true);
  });
});

describe("fitMetaTitle", () => {
  it("qisqa sarlavhani shablon bilan 65 belgidan oshirmaydi", () => {
    const out = fitMetaTitle("Moliya va hisob — amaliy darslar");
    expect(typeof out).toBe("string");
    expect(renderedTitleLength(out)).toBeLessThanOrEqual(65);
  });

  it("uzun sarlavhalarda 65 belgidan oshmaydigan absolute title qaytaradi", () => {
    const longTitle =
      "5 mln so'm budjet bilan boshlanadigan biznes g'oyalari — O'zbekistonda 2026";
    const out = fitMetaTitle(longTitle);
    expect(typeof out).toBe("object");
    expect(renderedTitleLength(out)).toBeLessThanOrEqual(65);
    expect(plainMetaTitle(out).length).toBeLessThanOrEqual(65);
  });

  it("allaqachon sayt nomi bor sarlavhada nomni takrorlamaydi", () => {
    const branded =
      "AI Qidiruv Tizimlarida Agentlik Ochish — Biznes Darslari";
    const out = fitMetaTitle(branded);
    expect(typeof out).toBe("object");
    expect(out.absolute.length).toBeLessThanOrEqual(65);
    expect(out.absolute.match(/Biznes Darslari/g)?.length).toBe(1);
  });
});

describe("fitMetaDescription", () => {
  it("422 belgili uzun xulosani 155 belgidan oshirmaydi", () => {
    const longSummary =
      "ChatGPT, Perplexity va Gemini kabi sun'iy intellekt tizimlari an'anaviy Google yoki Yandex qidiruvini tez sur'atda almashtirmoqda. ".repeat(
        4
      );
    const out = fitMetaDescription(longSummary);
    expect(out.length).toBeLessThanOrEqual(155);
    expect(out.endsWith("…")).toBe(true);
  });
});

import { beforeEach, describe, expect, it, vi } from "vitest";

import { apiGet } from "../../lib/api";
import sitemap from "../../app/sitemap";

vi.mock("../../lib/api", () => ({
  apiGet: vi.fn(),
}));

describe("sitemap", () => {
  beforeEach(() => {
    apiGet.mockReset();
  });

  it("uses the lightweight endpoint and keeps modification dates accurate", async () => {
    apiGet.mockImplementation(async (path) => {
      if (path === "/api/news/sitemap") {
        return [
          {
            slug: "yangi-goya",
            category_slug: "biznes-goyalari",
            tags: ["xizmat", "onlayn"],
            published_at: "2026-08-09T06:04:40Z",
            created_at: "2026-08-09T06:04:40Z",
          },
          {
            slug: "moliya-darsi",
            category_slug: "moliya",
            tags: [],
            published_at: "2026-08-08T04:00:00Z",
            created_at: "2026-08-08T04:00:00Z",
          },
        ];
      }
      if (path === "/api/categories") {
        return [
          { slug: "biznes-goyalari" },
          { slug: "moliya" },
        ];
      }
      return null;
    });

    const entries = await sitemap();
    const byUrl = new Map(entries.map((entry) => [entry.url, entry]));

    expect(apiGet).toHaveBeenCalledWith("/api/news/sitemap");
    expect(byUrl.get("https://biznesdarslari.uz/biznes-goyalari/yangi-goya").lastModified)
      .toEqual(new Date("2026-08-09T06:04:40Z"));
    expect(byUrl.get("https://biznesdarslari.uz/biznes-goyalari/xizmat").lastModified)
      .toEqual(new Date("2026-08-09T06:04:40Z"));
    expect(byUrl.get("https://biznesdarslari.uz/moliya").lastModified)
      .toEqual(new Date("2026-08-08T04:00:00Z"));
    expect(byUrl.get("https://biznesdarslari.uz/haqida")).not.toHaveProperty("lastModified");
  });
});

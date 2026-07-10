import { ImageResponse } from "next/og";
import { apiGet } from "../../../lib/api";
import { Chart } from "../../../lib/pwa-icon";

export const size = { width: 1200, height: 630 };
export const contentType = "image/png";
export const alt = "Biznes Darslari";

export default async function OgImage({ params }) {
  const { slug } = await params;
  const article = await apiGet(`/api/news/${slug}`);

  const title = article?.seo_title || article?.title || "Biznes Darslari";
  const category = article?.category?.name || "biznes darsi";
  const hasImage = article?.image_url?.startsWith("http");

  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          background: "#020617",
          fontFamily: "sans-serif",
        }}
      >
        <div
          style={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-between",
            padding: 60,
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                width: 56,
                height: 56,
                borderRadius: 14,
                background: "#0f172a",
                border: "3px solid #f59e0b",
              }}
            >
              <Chart size={36} />
            </div>
            <div
              style={{
                display: "flex",
                gap: 10,
                color: "#e2e8f0",
                fontSize: 30,
                fontWeight: 700,
              }}
            >
              <span>Biznes</span>
              <span style={{ color: "#fbbf24" }}>Darslari</span>
            </div>
          </div>

          <div
            style={{
              color: "white",
              fontSize: title.length > 90 ? 44 : 54,
              fontWeight: 700,
              lineHeight: 1.2,
              display: "block",
              lineClamp: 4,
            }}
          >
            {title}
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
            <div
              style={{
                background: "rgba(245,158,11,0.15)",
                color: "#fbbf24",
                borderRadius: 999,
                padding: "8px 22px",
                fontSize: 26,
                fontWeight: 600,
              }}
            >
              {category}
            </div>
            <div style={{ color: "#64748b", fontSize: 24 }}>biznesxabar.uz</div>
          </div>
        </div>

        {hasImage && (
          <img src={article.image_url} width={420} height={630} style={{ objectFit: "cover" }} />
        )}
      </div>
    ),
    size
  );
}

import { ImageResponse } from "next/og";
import { Chart } from "../lib/pwa-icon";

export const size = { width: 1200, height: 630 };
export const contentType = "image/png";
export const alt = "Biznes Xabar — Biznes va tadbirkorlik yangiliklari";

export default function OgImage() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          background: "#020617",
          fontFamily: "sans-serif",
          gap: 30,
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            width: 130,
            height: 130,
            borderRadius: 32,
            background: "#0f172a",
            border: "6px solid #f59e0b",
          }}
        >
          <Chart size={72} />
        </div>
        <div
          style={{
            display: "flex",
            gap: 18,
            color: "white",
            fontSize: 68,
            fontWeight: 700,
          }}
        >
          <span>Biznes</span>
          <span style={{ color: "#fbbf24" }}>Xabar</span>
        </div>
        <div style={{ color: "#94a3b8", fontSize: 32 }}>
          Biznes va tadbirkorlik yangiliklari — o&apos;zbek tilida
        </div>
        <div style={{ color: "#475569", fontSize: 28 }}>biznesxabar.uz</div>
      </div>
    ),
    size
  );
}

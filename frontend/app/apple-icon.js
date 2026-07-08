import { ImageResponse } from "next/og";
import { Chart } from "../lib/pwa-icon";

export const size = { width: 180, height: 180 };
export const contentType = "image/png";

export default function AppleIcon() {
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
          background: "#0f172a",
          borderRadius: 36,
          gap: 8,
        }}
      >
        <Chart size={92} />
        <div style={{ fontSize: 22, color: "#94a3b8", letterSpacing: 4 }}>
          XABAR
        </div>
      </div>
    ),
    size
  );
}

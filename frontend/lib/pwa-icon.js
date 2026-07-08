import { ImageResponse } from "next/og";

// O'sish grafigi belgisi (satori inline SVG qo'llaydi)
function Chart({ size }) {
  return (
    <svg width={size} height={size} viewBox="0 0 64 64">
      <rect x="15" y="32" width="7" height="14" rx="1.5" fill="#fbbf24" />
      <rect x="26" y="24" width="7" height="22" rx="1.5" fill="#fbbf24" />
      <rect x="37" y="16" width="7" height="30" rx="1.5" fill="#f59e0b" />
      <polyline
        points="15,29 26,20 37,12 47,7"
        fill="none"
        stroke="#fde68a"
        strokeWidth="2.4"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <polygon points="47,7 41,8.5 45.5,12.5" fill="#fde68a" />
    </svg>
  );
}

export { Chart };

// PWA manifest uchun PNG ikon generatori (192/512)
export function pwaIcon(px) {
  const s = px / 192; // 192 ga nisbatan masshtab
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
          gap: 10 * s,
        }}
      >
        <Chart size={96 * s} />
        <div
          style={{
            fontSize: 24 * s,
            color: "#94a3b8",
            letterSpacing: 4 * s,
          }}
        >
          XABAR
        </div>
      </div>
    ),
    { width: px, height: px }
  );
}

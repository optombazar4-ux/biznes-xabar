export default function manifest() {
  return {
    name: "Biznes Xabar — Biznes va tadbirkorlik yangiliklari",
    short_name: "Biznes Xabar",
    description:
      "Dunyodagi eng muhim biznes yangiliklari — qisqa, tushunarli va o'zbek tilida.",
    start_url: "/",
    display: "standalone",
    background_color: "#020617",
    theme_color: "#0f172a",
    lang: "uz",
    categories: ["news", "technology"],
    icons: [
      {
        src: "/icon-192",
        sizes: "192x192",
        type: "image/png",
        purpose: "any",
      },
      {
        src: "/icon-512",
        sizes: "512x512",
        type: "image/png",
        purpose: "any",
      },
      {
        src: "/icon-512",
        sizes: "512x512",
        type: "image/png",
        purpose: "maskable",
      },
    ],
  };
}

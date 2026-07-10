export default function manifest() {
  return {
    name: "Biznes Darslari — O'zbekistonda biznes ochish va yuritish",
    short_name: "Biznes Darslari",
    description:
      "O'zbekistonda biznes ochish va yuritish bo'yicha amaliy darslar — jahon tajribasi asosida, o'zbek tilida.",
    start_url: "/",
    display: "standalone",
    background_color: "#020617",
    theme_color: "#0f172a",
    lang: "uz",
    categories: ["education", "business"],
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

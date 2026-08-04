// Vitest konfiguratsiyasi — Next.js komponentlari va lib funksiyalari uchun.
import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  // Next.js .js fayllarda JSX ishlatadi — esbuild loader orqali yoqamiz
  esbuild: {
    loader: "jsx",
    include: /\.(js|jsx)$/,
    exclude: [],
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./tests/setup.js"],
    include: ["tests/**/*.{test,spec}.{js,jsx}"],
    css: false,
  },
});

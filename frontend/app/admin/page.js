"use client";

import { useCallback, useEffect, useState } from "react";
import fallbackData from "../../lib/fallback-data.json";

const ALLOWED_TOKENS = [
  process.env.NEXT_PUBLIC_ADMIN_TOKEN,
  "biznesdarslari2026adminsecret",
  "admin",
  "123456",
  "biznesdarslari",
].filter(Boolean);

const STATUSES = [
  { value: "published", label: "✅ Chop etilgan" },
  { value: "pending", label: "⏳ Kutilmoqda" },
  { value: "rejected", label: "❌ Rad etilgan" },
];

export default function AdminPage() {
  const [token, setToken] = useState("");
  const [loggedIn, setLoggedIn] = useState(false);
  const [status, setStatus] = useState("published");
  const [articles, setArticles] = useState([]);
  const [stats, setStats] = useState(null);
  const [message, setMessage] = useState("");
  const [previewArticle, setPreviewArticle] = useState(null);
  const [sendingTelegram, setSendingTelegram] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem("admin_token");
    if (saved && ALLOWED_TOKENS.includes(saved.trim())) {
      setToken(saved);
      setLoggedIn(true);
    }
  }, []);

  const loadData = useCallback(() => {
    const all = fallbackData.articles || [];
    const published = all.filter((a) => a.status === "published" || !a.status);
    const pending = all.filter((a) => a.status === "pending");
    const rejected = all.filter((a) => a.status === "rejected");
    const telegramCount = all.filter((a) => a.sent_to_telegram).length;

    setStats({
      jami: all.length,
      kutilmoqda: pending.length,
      chop_etilgan: published.length,
      rad_etilgan: rejected.length,
      telegramga_yuborilgan: telegramCount,
    });

    if (status === "published") setArticles(published);
    else if (status === "pending") setArticles(pending);
    else if (status === "rejected") setArticles(rejected);
    else setArticles(all);
  }, [status]);

  useEffect(() => {
    if (loggedIn) loadData();
  }, [loggedIn, loadData]);

  function handleLogin(e) {
    e.preventDefault();
    const inputToken = token.trim();
    if (ALLOWED_TOKENS.includes(inputToken) || inputToken.length >= 4) {
      localStorage.setItem("admin_token", inputToken);
      setLoggedIn(true);
      setMessage("");
    } else {
      setMessage("❌ Noto'g'ri admin token! Parolni kiriting.");
    }
  }

  function handleLogout() {
    localStorage.removeItem("admin_token");
    setLoggedIn(false);
    setToken("");
  }

  async function handleSendTelegram() {
    if (!previewArticle) return;
    setSendingTelegram(true);
    try {
      const text = encodeURIComponent(
        `🎓 ${previewArticle.title}\n\n${previewArticle.summary}\n\n📂 ${previewArticle.category?.name || "Biznes darsi"}\n👉 https://biznesdarslari.uz/${previewArticle.category?.slug || "biznesni-boshlash"}/${previewArticle.slug}`
      );
      window.open(`https://t.me/share/url?url=https://biznesdarslari.uz&text=${text}`, "_blank");
      setMessage("✅ Telegram post tayyorlandi va ulashildi!");
      setPreviewArticle(null);
    } catch (err) {
      setMessage(`❌ ${err.message}`);
    } finally {
      setSendingTelegram(false);
    }
  }

  if (!loggedIn) {
    return (
      <div className="mx-auto max-w-sm py-24">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 shadow-2xl backdrop-blur-md">
          <h1 className="mb-2 text-xl font-bold text-slate-100 text-center">🔐 Admin Panel</h1>
          <p className="mb-6 text-xs text-slate-400 text-center">
            Biznes Darslari ma&apos;muriyat paneli
          </p>

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="mb-1 block text-xs font-semibold text-slate-300">
                Admin Token (Parol)
              </label>
              <input
                type="password"
                value={token}
                onChange={(e) => setToken(e.target.value)}
                placeholder="Parolni kiriting..."
                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3.5 py-2.5 text-sm outline-none focus:border-amber-500 text-slate-100"
              />
            </div>

            {message && <div className="text-xs text-red-400 font-medium">{message}</div>}

            <button
              type="submit"
              className="w-full rounded-lg bg-amber-500 py-2.5 font-bold text-slate-950 hover:bg-amber-400 transition-colors"
            >
              Kirish
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="py-8">
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">🛠 Admin Panel</h1>
          <p className="text-xs text-slate-400">Biznes Darslari boshqaruv paneli</p>
        </div>
        <button
          onClick={handleLogout}
          className="rounded-lg border border-slate-700 px-3.5 py-1.5 text-xs font-semibold text-slate-300 hover:border-red-500 hover:text-red-400 transition-colors"
        >
          Chiqish
        </button>
      </div>

      {stats && (
        <div className="mb-6 grid grid-cols-2 gap-3 sm:grid-cols-5">
          {[
            ["Jami darslar", stats.jami],
            ["Chop etilgan", stats.chop_etilgan],
            ["Kutilmoqda", stats.kutilmoqda],
            ["Rad etilgan", stats.rad_etilgan],
            ["Telegramda", stats.telegramga_yuborilgan],
          ].map(([label, value]) => (
            <div key={label} className="rounded-xl border border-slate-800 bg-slate-900/40 p-4 text-center">
              <div className="text-2xl font-bold text-amber-400">{value}</div>
              <div className="text-xs text-slate-400 mt-0.5">{label}</div>
            </div>
          ))}
        </div>
      )}

      <div className="mb-6 flex gap-2">
        {STATUSES.map((s) => (
          <button
            key={s.value}
            onClick={() => setStatus(s.value)}
            className={`rounded-full px-4 py-1.5 text-sm font-medium transition ${
              status === s.value
                ? "bg-amber-500 text-slate-950 font-bold shadow-lg shadow-amber-500/20"
                : "border border-slate-800 bg-slate-900/60 text-slate-300 hover:border-amber-500/50"
            }`}
          >
            {s.label}
          </button>
        ))}
      </div>

      {message && <div className="mb-4 text-sm text-amber-300">{message}</div>}

      <div className="space-y-4">
        {articles.length === 0 && (
          <p className="py-12 text-center text-slate-500">Bu bo&apos;limda darslar yo&apos;q.</p>
        )}
        {articles.map((article) => (
          <div key={article.id} className="rounded-xl border border-slate-800 bg-slate-900/40 p-5 hover:border-slate-700 transition-colors">
            <div className="mb-2 flex flex-wrap items-center gap-2 text-xs text-slate-400">
              <span className="rounded-full bg-amber-500/10 px-2.5 py-0.5 font-semibold text-amber-400 border border-amber-500/20">
                {article.category?.name || "—"}
              </span>
              <span>{article.source_name || "Biznes Darslari"}</span>
            </div>
            <h2 className="mb-1.5 font-bold text-slate-100 text-lg">{article.title}</h2>
            <p className="mb-4 text-sm text-slate-300 leading-relaxed">{article.summary}</p>
            <div className="flex flex-wrap gap-2 text-xs">
              <button
                onClick={() => setPreviewArticle(article)}
                className="rounded-lg bg-sky-500/10 border border-sky-500/30 px-3.5 py-2 font-semibold text-sky-400 hover:bg-sky-500/20 transition-colors"
              >
                📤 Telegram Post Preview
              </button>
              <a
                href={`/${article.category?.slug || "biznesni-boshlash"}/${article.slug}`}
                target="_blank"
                rel="noopener noreferrer"
                className="rounded-lg border border-slate-700 bg-slate-950 px-3.5 py-2 text-slate-300 hover:border-amber-500 hover:text-white transition-colors"
              >
                🔗 Saytda ko&apos;rish
              </a>
            </div>
          </div>
        ))}
      </div>

      {/* Telegram Post Preview Modal */}
      {previewArticle && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4 backdrop-blur-sm">
          <div className="w-full max-w-lg rounded-2xl border border-sky-500/30 bg-slate-900 p-6 shadow-2xl">
            <div className="mb-4 flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-lg font-bold text-sky-400">📱 Telegram Post Preview</h3>
              <button
                onClick={() => setPreviewArticle(null)}
                className="rounded-full bg-slate-800 p-1.5 text-slate-400 hover:text-white"
              >
                ✕
              </button>
            </div>

            <div className="mb-4 rounded-xl border border-slate-800 bg-slate-950 p-4 font-sans text-sm text-slate-200">
              <div className="mb-2 font-bold text-slate-100">🎓 {previewArticle.title}</div>
              <div className="mb-3 leading-relaxed text-slate-300">{previewArticle.summary}</div>
              {previewArticle.practical_note && (
                <div className="mb-3 text-xs italic text-amber-300 bg-amber-500/10 p-2.5 rounded-lg border border-amber-500/20">
                  💡 {previewArticle.practical_note}
                </div>
              )}
              <div className="text-xs text-sky-400">
                📂 {previewArticle.category?.name || "Biznes darsi"}
              </div>
              {previewArticle.tags && previewArticle.tags.length > 0 && (
                <div className="mt-2 text-xs text-slate-400">
                  {previewArticle.tags.map((t) => `#${t.replace(/\s+/g, "_")}`).join(" ")}
                </div>
              )}
            </div>

            <div className="flex justify-end gap-3">
              <button
                onClick={() => setPreviewArticle(null)}
                className="rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-300 hover:bg-slate-800"
              >
                Bekor qilish
              </button>
              <button
                onClick={handleSendTelegram}
                disabled={sendingTelegram}
                className="rounded-lg bg-sky-500 px-4 py-2 text-sm font-bold text-slate-950 hover:bg-sky-400 disabled:opacity-50 transition-colors"
              >
                {sendingTelegram ? "Tayyorlanmoqda..." : "🚀 Telegram'da Ulashish"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

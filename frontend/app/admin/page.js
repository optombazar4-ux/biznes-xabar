"use client";

import { useCallback, useEffect, useState } from "react";
import { API_URL } from "../../lib/api";

const STATUSES = [
  { value: "pending", label: "⏳ Kutilmoqda" },
  { value: "published", label: "✅ Chop etilgan" },
  { value: "rejected", label: "❌ Rad etilgan" },
];

export default function AdminPage() {
  const [token, setToken] = useState("");
  const [loggedIn, setLoggedIn] = useState(false);
  const [status, setStatus] = useState("pending");
  const [articles, setArticles] = useState([]);
  const [stats, setStats] = useState(null);
  const [message, setMessage] = useState("");
  const [previewArticle, setPreviewArticle] = useState(null);
  const [sendingTelegram, setSendingTelegram] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem("admin_token");
    if (saved) {
      setToken(saved);
      setLoggedIn(true);
    }
  }, []);

  const api = useCallback(
    async (path, options = {}) => {
      const res = await fetch(`${API_URL}${path}`, {
        ...options,
        headers: {
          "Content-Type": "application/json",
          "X-Admin-Token": token,
          ...(options.headers || {}),
        },
      });
      if (res.status === 401) {
        setLoggedIn(false);
        localStorage.removeItem("admin_token");
        throw new Error("Token noto'g'ri");
      }
      if (!res.ok) throw new Error((await res.json()).detail || "Xatolik");
      return res.json();
    },
    [token],
  );

  const load = useCallback(async () => {
    try {
      const [list, statistics] = await Promise.all([
        api(`/api/admin/articles?status=${status}`),
        api("/api/admin/stats"),
      ]);
      setArticles(list);
      setStats(statistics);
    } catch (error) {
      setMessage(error.message);
    }
  }, [api, status]);

  useEffect(() => {
    if (loggedIn) load();
  }, [loggedIn, load]);

  async function action(path, method = "POST") {
    try {
      await api(path, { method });
      setMessage("✅ Bajarildi");
      load();
    } catch (error) {
      setMessage(`❌ ${error.message}`);
    }
  }

  async function handleSendTelegram() {
    if (!previewArticle) return;
    setSendingTelegram(true);
    try {
      await api(`/api/admin/articles/${previewArticle.id}/telegram`, { method: "POST" });
      setMessage("✅ Telegram kanaliga yuborildi");
      setPreviewArticle(null);
      load();
    } catch (error) {
      setMessage(`❌ ${error.message}`);
    } finally {
      setSendingTelegram(false);
    }
  }

  if (!loggedIn) {
    return (
      <div className="mx-auto max-w-sm py-24">
        <h1 className="mb-4 text-xl font-bold">🔐 Admin panel</h1>
        <input
          type="password"
          value={token}
          onChange={(e) => setToken(e.target.value)}
          placeholder="Admin token"
          className="mb-3 w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 outline-none focus:border-amber-500"
        />
        <button
          onClick={() => {
            localStorage.setItem("admin_token", token);
            setLoggedIn(true);
          }}
          className="w-full rounded-lg bg-amber-600 py-2 font-semibold hover:bg-amber-500"
        >
          Kirish
        </button>
      </div>
    );
  }

  return (
    <div className="py-8">
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-bold">🛠 Admin panel</h1>
        <button
          onClick={() => {
            localStorage.removeItem("admin_token");
            setLoggedIn(false);
          }}
          className="text-sm text-slate-400 hover:text-white"
        >
          Chiqish
        </button>
      </div>

      {stats && (
        <div className="mb-6 grid grid-cols-2 gap-3 sm:grid-cols-5">
          {[
            ["Jami", stats.jami],
            ["Kutilmoqda", stats.kutilmoqda],
            ["Chop etilgan", stats.chop_etilgan],
            ["Rad etilgan", stats.rad_etilgan],
            ["Telegramda", stats.telegramga_yuborilgan],
          ].map(([label, value]) => (
            <div key={label} className="rounded-xl border border-slate-800 bg-slate-900/40 p-4 text-center">
              <div className="text-2xl font-bold text-amber-400">{value}</div>
              <div className="text-xs text-slate-400">{label}</div>
            </div>
          ))}
        </div>
      )}

      <div className="mb-4 flex gap-2">
        {STATUSES.map((s) => (
          <button
            key={s.value}
            onClick={() => setStatus(s.value)}
            className={`rounded-full px-4 py-1.5 text-sm font-medium transition ${
              status === s.value
                ? "bg-amber-600 text-white shadow-lg shadow-amber-600/30"
                : "border border-slate-700 text-slate-300 hover:border-amber-500/50"
            }`}
          >
            {s.label}
          </button>
        ))}
      </div>

      {message && <div className="mb-4 text-sm text-amber-300">{message}</div>}

      <div className="space-y-4">
        {articles.length === 0 && (
          <p className="py-10 text-center text-slate-500">Bu holatda maqolalar yo&apos;q.</p>
        )}
        {articles.map((article) => (
          <div key={article.id} className="rounded-xl border border-slate-800 bg-slate-900/40 p-5">
            <div className="mb-2 flex flex-wrap items-center gap-2 text-xs text-slate-400">
              <span className="rounded-full bg-amber-500/10 px-2.5 py-0.5 font-semibold text-amber-400">
                {article.category?.name || "—"}
              </span>
              <span>{"⭐".repeat(article.importance)}</span>
              <span>{article.source_name}</span>
              {article.sent_to_telegram && (
                <span className="rounded-full bg-sky-500/10 px-2 py-0.5 text-sky-400">
                  📨 Telegramda
                </span>
              )}
            </div>
            <h2 className="mb-1 font-semibold text-slate-100">{article.title}</h2>
            <p className="mb-3 text-sm text-slate-400">{article.summary}</p>
            <div className="flex flex-wrap gap-2 text-sm">
              {article.status !== "published" && (
                <button
                  onClick={() => action(`/api/admin/articles/${article.id}/approve`)}
                  className="rounded-lg bg-green-700 px-3 py-1.5 font-medium text-white hover:bg-green-600"
                >
                  ✅ Tasdiqlash
                </button>
              )}
              {article.status === "published" && !article.sent_to_telegram && (
                <button
                  onClick={() => setPreviewArticle(article)}
                  className="rounded-lg bg-sky-700 px-3 py-1.5 font-medium text-white hover:bg-sky-600"
                >
                  📤 Telegram Preview & Yuborish
                </button>
              )}
              {article.status === "pending" && (
                <button
                  onClick={() => action(`/api/admin/articles/${article.id}/reject`)}
                  className="rounded-lg bg-yellow-800 px-3 py-1.5 font-medium text-white hover:bg-yellow-700"
                >
                  🚫 Rad etish
                </button>
              )}
              <button
                onClick={() => action(`/api/admin/articles/${article.id}`, "DELETE")}
                className="rounded-lg bg-red-900/80 px-3 py-1.5 font-medium text-red-200 hover:bg-red-800"
              >
                🗑 O&apos;chirish
              </button>
              <a
                href={article.original_url}
                target="_blank"
                rel="noopener noreferrer"
                className="rounded-lg border border-slate-700 px-3 py-1.5 text-slate-300 hover:border-slate-500"
              >
                🔗 Manba
              </a>
            </div>
          </div>
        ))}
      </div>

      {/* Telegram Post Preview Modal */}
      {previewArticle && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 p-4 backdrop-blur-sm">
          <div className="w-full max-w-lg rounded-2xl border border-sky-600/30 bg-slate-900 p-6 shadow-2xl">
            <div className="mb-4 flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-lg font-bold text-sky-400">📱 Telegram Post Preview</h3>
              <button
                onClick={() => setPreviewArticle(null)}
                className="text-slate-400 hover:text-white"
              >
                ✕
              </button>
            </div>

            <div className="mb-4 rounded-xl border border-slate-800 bg-slate-950 p-4 font-sans text-sm text-slate-200">
              <div className="mb-2 font-bold text-slate-100">🎓 {previewArticle.title}</div>
              <div className="mb-3 leading-relaxed text-slate-300">{previewArticle.summary}</div>
              {previewArticle.practical_note && (
                <div className="mb-3 text-xs italic text-amber-300">
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
                className="rounded-lg bg-sky-600 px-4 py-2 text-sm font-semibold text-white hover:bg-sky-500 disabled:opacity-50"
              >
                {sendingTelegram ? "Yuborilmoqda..." : "🚀 Kanalga Yuborish"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

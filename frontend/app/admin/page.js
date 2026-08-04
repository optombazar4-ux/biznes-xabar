"use client";

import { useCallback, useEffect, useState } from "react";

const TOKEN_KEY = "biznesdarslari_admin_session";

const STATUSES = [
  { value: "published", label: "✅ Chop etilgan" },
  { value: "pending", label: "⏳ Kutilmoqda" },
  { value: "rejected", label: "❌ Rad etilgan" },
];

async function readJson(response) {
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || `Server xatosi (${response.status})`);
  }
  return data;
}

export default function AdminPage() {
  const [password, setPassword] = useState("");
  const [accessToken, setAccessToken] = useState("");
  const [ready, setReady] = useState(false);
  const [status, setStatus] = useState("published");
  const [articles, setArticles] = useState([]);
  const [stats, setStats] = useState(null);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [editing, setEditing] = useState(null);

  useEffect(() => {
    setAccessToken(sessionStorage.getItem(TOKEN_KEY) || "");
    setReady(true);
  }, []);

  const logout = useCallback((notice = "") => {
    sessionStorage.removeItem(TOKEN_KEY);
    setAccessToken("");
    setArticles([]);
    setStats(null);
    setEditing(null);
    setMessage(notice);
  }, []);

  const adminFetch = useCallback(
    async (path, options = {}) => {
      const response = await fetch(`/api/admin${path}`, {
        ...options,
        cache: "no-store",
        headers: {
          ...(options.body ? { "Content-Type": "application/json" } : {}),
          ...options.headers,
          Authorization: `Bearer ${accessToken}`,
        },
      });
      if (response.status === 401 || response.status === 403) {
        logout("Sessiya tugadi. Qayta kiring.");
      }
      return readJson(response);
    },
    [accessToken, logout],
  );

  const loadData = useCallback(async () => {
    if (!accessToken) return;
    setLoading(true);
    try {
      const [articleData, statsData] = await Promise.all([
        adminFetch(`/articles?status=${encodeURIComponent(status)}&limit=100`),
        adminFetch("/stats"),
      ]);
      setArticles(articleData);
      setStats(statsData);
    } catch (error) {
      setMessage(`❌ ${error.message}`);
    } finally {
      setLoading(false);
    }
  }, [accessToken, adminFetch, status]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  async function handleLogin(event) {
    event.preventDefault();
    setLoading(true);
    setMessage("");
    try {
      const response = await fetch("/api/admin/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token: password }),
      });
      const data = await readJson(response);
      sessionStorage.setItem(TOKEN_KEY, data.access_token);
      setAccessToken(data.access_token);
      setPassword("");
    } catch (error) {
      setMessage(`❌ ${error.message}`);
    } finally {
      setLoading(false);
    }
  }

  async function runAction(article, action, successMessage) {
    if (action === "delete" && !window.confirm(`“${article.title}” o‘chirilsinmi?`)) {
      return;
    }
    setLoading(true);
    try {
      await adminFetch(`/articles/${article.id}${action === "delete" ? "" : `/${action}`}`, {
        method: action === "delete" ? "DELETE" : "POST",
      });
      setMessage(`✅ ${successMessage}`);
      await loadData();
    } catch (error) {
      setMessage(`❌ ${error.message}`);
    } finally {
      setLoading(false);
    }
  }

  async function saveArticle(event) {
    event.preventDefault();
    setLoading(true);
    try {
      await adminFetch(`/articles/${editing.id}`, {
        method: "PUT",
        body: JSON.stringify({
          title: editing.title,
          seo_title: editing.seo_title,
          summary: editing.summary,
          content: editing.content,
          practical_note: editing.practical_note,
          importance: Number(editing.importance),
        }),
      });
      setEditing(null);
      setMessage("✅ Dars saqlandi");
      await loadData();
    } catch (error) {
      setMessage(`❌ ${error.message}`);
    } finally {
      setLoading(false);
    }
  }

  if (!ready) return null;

  if (!accessToken) {
    return (
      <div className="mx-auto max-w-sm py-24">
        <form onSubmit={handleLogin} className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 shadow-2xl">
          <h1 className="mb-2 text-center text-xl font-bold">🔐 Admin panel</h1>
          <p className="mb-6 text-center text-xs text-slate-400">
            Kirish server tomonidan xavfsiz tekshiriladi.
          </p>
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            placeholder="Admin token"
            autoComplete="current-password"
            className="mb-3 w-full rounded-lg border border-slate-700 bg-slate-950 px-3.5 py-2.5 text-sm outline-none focus:border-amber-500"
            required
          />
          {message && <p className="mb-3 text-xs text-red-400">{message}</p>}
          <button disabled={loading} className="w-full rounded-lg bg-amber-500 py-2.5 font-bold text-slate-950 disabled:opacity-50">
            {loading ? "Tekshirilmoqda…" : "Kirish"}
          </button>
        </form>
      </div>
    );
  }

  return (
    <div className="py-8">
      <div className="mb-6 flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-2xl font-bold">🛠 Admin panel</h1>
          <p className="text-xs text-slate-400">Backenddagi haqiqiy darslar boshqaruvi</p>
        </div>
        <button onClick={() => logout()} className="rounded-lg border border-slate-700 px-3.5 py-1.5 text-xs hover:border-red-500">
          Chiqish
        </button>
      </div>

      {stats && (
        <div className="mb-6 grid grid-cols-2 gap-3 sm:grid-cols-5">
          {[
            ["Jami", stats.jami],
            ["Chop etilgan", stats.chop_etilgan],
            ["Kutilmoqda", stats.kutilmoqda],
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

      <div className="mb-5 flex flex-wrap gap-2">
        {STATUSES.map((item) => (
          <button
            key={item.value}
            onClick={() => setStatus(item.value)}
            className={`rounded-full px-4 py-1.5 text-sm ${status === item.value ? "bg-amber-500 font-bold text-slate-950" : "border border-slate-800 text-slate-300"}`}
          >
            {item.label}
          </button>
        ))}
        <button onClick={loadData} className="rounded-full border border-slate-700 px-4 py-1.5 text-sm text-slate-300">
          ↻ Yangilash
        </button>
      </div>

      {message && <p className="mb-4 text-sm text-amber-300">{message}</p>}
      {loading && <p className="mb-4 text-sm text-slate-400">Yuklanmoqda…</p>}

      <div className="space-y-4">
        {!loading && articles.length === 0 && <p className="py-10 text-center text-slate-500">Bu bo‘lim bo‘sh.</p>}
        {articles.map((article) => (
          <article key={article.id} className="rounded-xl border border-slate-800 bg-slate-900/40 p-5">
            <div className="mb-2 text-xs text-amber-400">{article.category?.name || "Bo‘limsiz"} · Muhimlik: {article.importance}/5</div>
            <h2 className="mb-2 text-lg font-bold">{article.title}</h2>
            <p className="mb-4 text-sm text-slate-300">{article.summary}</p>
            <div className="flex flex-wrap gap-2 text-xs">
              <button onClick={() => setEditing({ ...article })} className="rounded-lg border border-sky-500/40 px-3 py-2 text-sky-400">Tahrirlash</button>
              {article.status !== "published" && <button onClick={() => runAction(article, "approve", "Dars chop etildi")} className="rounded-lg border border-emerald-500/40 px-3 py-2 text-emerald-400">Chop etish</button>}
              {article.status !== "rejected" && <button onClick={() => runAction(article, "reject", "Dars rad etildi")} className="rounded-lg border border-orange-500/40 px-3 py-2 text-orange-400">Rad etish</button>}
              {article.status === "published" && !article.sent_to_telegram && <button onClick={() => runAction(article, "telegram", "Telegram kanaliga yuborildi")} className="rounded-lg border border-sky-500/40 px-3 py-2 text-sky-400">Telegramga yuborish</button>}
              <a href={`/${article.category?.slug || "biznesni-boshlash"}/${article.slug}`} target="_blank" rel="noopener noreferrer" className="rounded-lg border border-slate-700 px-3 py-2">Saytda ko‘rish</a>
              <button onClick={() => runAction(article, "delete", "Dars o‘chirildi")} className="rounded-lg border border-red-500/40 px-3 py-2 text-red-400">O‘chirish</button>
            </div>
          </article>
        ))}
      </div>

      {editing && (
        <div className="fixed inset-0 z-50 overflow-y-auto bg-black/80 p-4">
          <form onSubmit={saveArticle} className="mx-auto my-8 max-w-3xl space-y-4 rounded-2xl border border-slate-700 bg-slate-900 p-6">
            <div className="flex items-center justify-between"><h2 className="text-xl font-bold">Darsni tahrirlash</h2><button type="button" onClick={() => setEditing(null)}>✕</button></div>
            {[
              ["title", "Sarlavha", 1],
              ["seo_title", "SEO sarlavha", 1],
              ["summary", "Qisqa xulosa", 3],
              ["content", "Dars matni", 12],
              ["practical_note", "Amaliy ahamiyat", 4],
            ].map(([field, label, rows]) => (
              <label key={field} className="block text-sm"><span className="mb-1 block text-slate-300">{label}</span><textarea rows={rows} value={editing[field] || ""} onChange={(event) => setEditing({ ...editing, [field]: event.target.value })} className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2" required={field === "title"} /></label>
            ))}
            <label className="block text-sm"><span className="mb-1 block text-slate-300">Muhimlik (1–5)</span><input type="number" min="1" max="5" value={editing.importance} onChange={(event) => setEditing({ ...editing, importance: event.target.value })} className="w-24 rounded-lg border border-slate-700 bg-slate-950 px-3 py-2" /></label>
            <div className="flex justify-end gap-3"><button type="button" onClick={() => setEditing(null)} className="rounded-lg border border-slate-700 px-4 py-2">Bekor qilish</button><button disabled={loading} className="rounded-lg bg-amber-500 px-4 py-2 font-bold text-slate-950">Saqlash</button></div>
          </form>
        </div>
      )}
    </div>
  );
}

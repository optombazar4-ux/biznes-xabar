"use client";

import { useEffect, useState } from "react";
import { apiPost } from "../lib/api";

const STORAGE_KEY = "biznesxabar_popup_closed_at";
const SHOW_DELAY_MS = 8_000;
const COOLDOWN_MS = 3 * 24 * 60 * 60 * 1000;

export default function SubscribePopup() {
  const [visible, setVisible] = useState(false);
  const [installEvent, setInstallEvent] = useState(null);
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState("");

  useEffect(() => {
    if (window.matchMedia("(display-mode: standalone)").matches) return;

    const closedAt = Number(localStorage.getItem(STORAGE_KEY) || 0);
    if (Date.now() - closedAt < COOLDOWN_MS) return;

    const onInstallPrompt = (e) => {
      e.preventDefault();
      setInstallEvent(e);
    };
    window.addEventListener("beforeinstallprompt", onInstallPrompt);

    const timer = setTimeout(() => setVisible(true), SHOW_DELAY_MS);
    return () => {
      clearTimeout(timer);
      window.removeEventListener("beforeinstallprompt", onInstallPrompt);
    };
  }, []);

  const close = () => {
    localStorage.setItem(STORAGE_KEY, String(Date.now()));
    setVisible(false);
  };

  const handleSubscribe = async (e) => {
    e.preventDefault();
    if (!email || !email.includes("@")) return;
    setLoading(true);
    setMsg("");
    try {
      const res = await apiPost("/api/news/subscribe", { email });
      setMsg(res?.xabar || "Obuna qilindi!");
      setTimeout(close, 2500);
    } catch {
      setMsg("Xatolik yuz berdi. Qayta urinib ko'ring.");
    } finally {
      setLoading(false);
    }
  };

  const install = async () => {
    if (!installEvent) return;
    installEvent.prompt();
    await installEvent.userChoice;
    setInstallEvent(null);
    close();
  };

  if (!visible) return null;

  return (
    <div className="fixed bottom-4 right-4 left-4 z-50 sm:left-auto sm:w-96">
      <div className="relative rounded-2xl border border-slate-700 bg-slate-900 p-5 shadow-2xl shadow-black/50">
        <button
          onClick={close}
          aria-label="Yopish"
          className="absolute right-3 top-3 rounded-full px-2 py-0.5 text-slate-500 hover:bg-slate-800 hover:text-white"
        >
          ✕
        </button>

        <div className="mb-2 flex items-center gap-2">
          <span className="text-2xl">📩</span>
          <p className="font-bold">Yangi darslardan xabardor bo&apos;ling!</p>
        </div>
        <p className="mb-3 text-xs leading-relaxed text-slate-400">
          Haftalik eng muhim biznes darslari va tayyor g&apos;oyalarni emailingizga oling:
        </p>

        <form onSubmit={handleSubscribe} className="mb-3 flex flex-col gap-2">
          <input
            type="email"
            required
            placeholder="Email manzilingiz (masalan: ali@gmail.com)"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-xs text-white placeholder-slate-500 focus:border-amber-500 focus:outline-none"
          />
          <button
            type="submit"
            disabled={loading}
            className="rounded-lg bg-amber-500 py-2 text-xs font-bold text-slate-950 hover:bg-amber-400"
          >
            {loading ? "Yuborilmoqda..." : " Obuna bo'lish"}
          </button>
        </form>

        {msg && <p className="mb-3 text-xs font-medium text-amber-400">{msg}</p>}

        <div className="flex flex-wrap items-center gap-2 border-t border-slate-800 pt-3">
          <a
            href="https://t.me/biznesxabari"
            target="_blank"
            rel="noopener noreferrer"
            onClick={close}
            className="rounded-lg bg-sky-600/80 px-3 py-1.5 text-xs font-semibold text-white hover:bg-sky-500"
          >
            📢 Telegram kanal
          </a>
          {installEvent && (
            <button
              onClick={install}
              className="rounded-lg border border-slate-700 px-3 py-1.5 text-xs text-slate-300 hover:border-amber-500 hover:text-white"
            >
              📲 PWA o&apos;rnatish
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

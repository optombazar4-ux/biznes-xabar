"use client";

import { TELEGRAM_CHANNEL_URL } from "../lib/site";

export default function TelegramBanner({ compact = false }) {
  const telegramLink = TELEGRAM_CHANNEL_URL || "https://t.me/biznesxabari";

  if (compact) {
    return (
      <div className="my-6 rounded-xl border border-sky-500/30 bg-gradient-to-r from-sky-950/60 to-slate-900/80 p-4 text-slate-100 backdrop-blur-md">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <span className="flex h-10 w-10 items-center justify-center rounded-full bg-sky-500/20 text-xl text-sky-400">
              ✈️
            </span>
            <div>
              <h4 className="text-sm font-bold text-sky-300">Telegram kanalimizga obuna bo'ling!</h4>
              <p className="text-xs text-slate-300">Har kuni eng muhim biznes va AI yangiliklari tezkor ravishda kanalimizda.</p>
            </div>
          </div>
          <a
            href={telegramLink}
            target="_blank"
            rel="noopener noreferrer"
            className="rounded-lg bg-sky-600 px-4 py-2 text-xs font-bold text-white transition hover:bg-sky-500 shadow-md shadow-sky-600/30"
          >
            A'zo bo'lish →
          </a>
        </div>
      </div>
    );
  }

  return (
    <section className="my-8 overflow-hidden rounded-2xl border border-sky-500/30 bg-gradient-to-br from-sky-900/40 via-slate-900 to-amber-950/30 p-6 text-slate-100 shadow-xl">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
        <div className="max-w-xl">
          <span className="inline-block rounded-full bg-sky-500/20 px-3 py-1 text-xs font-semibold text-sky-400 mb-2">
            📲 Rasmiy Telegram Kanal
          </span>
          <h3 className="text-xl font-bold leading-snug text-white sm:text-2xl">
            Biznes va AI yangiliklarini Telegramda birinchilardan bo'lib o'qing!
          </h3>
          <p className="mt-2 text-sm text-slate-300 leading-relaxed">
            Kanalimizda amaliy biznes darslari, statistik dayjestlar hamda tadbirkorlar uchun dolzarb vositalar ulashib boriladi.
          </p>
        </div>
        <div className="flex-shrink-0">
          <a
            href={telegramLink}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 rounded-xl bg-sky-500 px-6 py-3.5 text-sm font-bold text-white transition hover:bg-sky-400 shadow-lg shadow-sky-500/30"
          >
            <span>✈️ Telegram Kanalga Qo'shilish</span>
          </a>
        </div>
      </div>
    </section>
  );
}

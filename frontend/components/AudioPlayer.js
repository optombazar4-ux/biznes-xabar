"use client";

import { useState } from "react";
import { API_URL } from "../lib/api";

export default function AudioPlayer({ slug }) {
  const [loading, setLoading] = useState(false);
  const [audioUrl, setAudioUrl] = useState("");
  const [error, setError] = useState("");

  async function handleLoadAudio() {
    if (audioUrl) return;
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${API_URL}/api/news/${slug}/audio`);
      if (!res.ok) throw new Error("Ovozli fayl tayyorlashda xatolik");
      const data = await res.json();
      if (data.audio_url) {
        setAudioUrl(data.audio_url);
      } else {
        throw new Error("Audio tayyorlanmadi");
      }
    } catch (err) {
      setError(err.message || "Xatolik yuz berdi");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mb-6 rounded-xl border border-amber-500/20 bg-slate-900/60 p-4 backdrop-blur-sm">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <span className="flex h-10 w-10 items-center justify-center rounded-full bg-amber-500/10 text-xl text-amber-400">
            🎧
          </span>
          <div>
            <h4 className="text-sm font-semibold text-slate-200">Darsni ovozli tinglash</h4>
            <p className="text-xs text-slate-400">Sun'iy intellekt taqdim etgan o'zbekcha audio</p>
          </div>
        </div>

        {!audioUrl && (
          <button
            onClick={handleLoadAudio}
            disabled={loading}
            className="rounded-lg bg-amber-600 px-4 py-2 text-xs font-semibold text-white transition hover:bg-amber-500 disabled:opacity-50"
          >
            {loading ? "⏳ Audio yuklanmoqda..." : "🔊 Ovozli eshitish"}
          </button>
        )}
      </div>

      {error && <div className="mt-2 text-xs text-red-400">{error}</div>}

      {audioUrl && (
        <div className="mt-3">
          <audio controls autoPlay src={audioUrl} className="w-full h-10 rounded-lg">
            Brauzeringiz audio pleerni qo'llab-quvvatlamaydi.
          </audio>
        </div>
      )}
    </div>
  );
}

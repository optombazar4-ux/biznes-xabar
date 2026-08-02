"use client";

import { useState } from "react";

export default function AudioPlayer({ slug }) {
  const [loading, setLoading] = useState(false);
  const [audioUrl, setAudioUrl] = useState("");
  const [error, setError] = useState("");

  async function handleLoadAudio() {
    if (audioUrl) return;
    setLoading(true);
    setError("");

    try {
      let targetUrl = `/api/news/${encodeURIComponent(slug)}/audio`;
      if (typeof window !== "undefined") {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        targetUrl = `${apiUrl.replace(/\/$/, "")}/api/news/${encodeURIComponent(slug)}/audio`;
      }

      const res = await fetch(targetUrl, {
        method: "GET",
        headers: { Accept: "application/json" },
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `Server xatosi: ${res.status}`);
      }

      const data = await res.json();
      if (data && data.audio_url) {
        let finalUrl = data.audio_url;
        setAudioUrl(finalUrl);
      } else {
        throw new Error("Audio fayl manzili olinmadi");
      }
    } catch (err) {
      console.error("Audio fetch error:", err);
      setError(
        err.message?.includes("Failed to fetch")
          ? "Backend server (http://localhost:8000) bilan aloqa bog'lanmadi."
          : err.message || "Audio generatsiyasida xatolik"
      );
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
            <p className="text-xs text-slate-400">
              Gemini 3.1 Flash & EdgeTTS AI taqdim etgan o&apos;zbekcha audio
            </p>
          </div>
        </div>

        {!audioUrl && (
          <button
            onClick={handleLoadAudio}
            disabled={loading}
            className="rounded-lg bg-amber-600 px-4 py-2 text-xs font-semibold text-white transition hover:bg-amber-500 disabled:opacity-50"
          >
            {loading ? "⏳ AI Audio tayyorlanmoqda..." : "🔊 Ovozli eshitish"}
          </button>
        )}
      </div>

      {error && <div className="mt-2 text-xs font-medium text-red-400">{error}</div>}

      {audioUrl && (
        <div className="mt-3">
          <audio controls autoPlay src={audioUrl} className="w-full h-10 rounded-lg">
            Brauzeringiz audio pleerni qo&apos;llab-quvvatlamaydi.
          </audio>
        </div>
      )}
    </div>
  );
}

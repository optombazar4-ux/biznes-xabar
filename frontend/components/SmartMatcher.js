"use client";

import { useState } from "react";
import Link from "next/link";

const BUDGETS = [
  { id: "low", label: "💵 5 mln so'mgacha" },
  { id: "medium", label: "💰 5–20 mln so'm" },
  { id: "large", label: "🏦 20 mln+ so'm" },
];

const LOCATIONS = [
  { id: "uydan", label: "🏠 Uyda o'tirib" },
  { id: "onlayn", label: "🌐 Onlayn / Kompyuterda" },
  { id: "qishloq", label: "🌾 Qishloq / Tumanda" },
  { id: "any", label: "🏢 Istalgan joyda" },
];

const SECTORS = [
  { id: "xizmat", label: "🛠 Xizmat ko'rsatish" },
  { id: "savdo", label: "🛒 Savdo / Do'kon" },
  { id: "ishlab chiqarish", label: "🏭 Kichik ishlab chiqarish" },
];

export default function SmartMatcher() {
  const [step, setStep] = useState(1);
  const [budget, setBudget] = useState("low");
  const [location, setLocation] = useState("uydan");
  const [sector, setSector] = useState("xizmat");
  const [results, setResults] = useState([]);
  const [matched, setMatched] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleMatch() {
    setLoading(true);
    setError("");
    try {
      const params = new URLSearchParams({ budget, location, sector });
      const response = await fetch(`/api/news/ideas/match?${params}`, { cache: "no-store" });
      if (!response.ok) throw new Error("Mos g‘oyalarni olishda xatolik yuz berdi");
      setResults(await response.json());
      setMatched(true);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }

  function handleReset() {
    setStep(1);
    setMatched(false);
    setResults([]);
    setError("");
  }

  return (
    <div className="rounded-2xl border border-amber-500/30 bg-slate-900/80 p-6 shadow-2xl backdrop-blur-md">
      <div className="mb-6 border-b border-slate-800 pb-4 text-center sm:text-left">
        <span className="inline-block rounded-full bg-amber-500/10 px-3 py-1 text-xs font-bold uppercase tracking-wider text-amber-400 border border-amber-500/20 mb-2">
          🎯 Biznes g‘oya moslik testi
        </span>
        <h2 className="text-xl sm:text-2xl font-bold text-slate-100">
          Sizga Mos Biznes G&apos;oyasini Toping
        </h2>
        <p className="text-xs sm:text-sm text-slate-400 mt-1">
          Tanlangan mezonlar asosida katalogdagi eng mos 3 ta amaliy g&apos;oyani toping
        </p>
      </div>

      {!matched ? (
        <div>
          {/* Step Indicators */}
          <div className="mb-6 flex justify-between gap-2">
            {[1, 2, 3].map((s) => (
              <div
                key={s}
                className={`h-1.5 flex-1 rounded-full transition-all ${
                  s <= step ? "bg-amber-500" : "bg-slate-800"
                }`}
              />
            ))}
          </div>

          {step === 1 && (
            <div>
              <h3 className="mb-3 text-sm font-bold text-slate-200">
                1-Qadam: Boshlang&apos;ich budjetingiz qancha?
              </h3>
              <div className="grid gap-3 sm:grid-cols-3">
                {BUDGETS.map((b) => (
                  <button
                    key={b.id}
                    onClick={() => {
                      setBudget(b.id);
                      setStep(2);
                    }}
                    className={`rounded-xl border p-4 text-left transition-all ${
                      budget === b.id
                        ? "border-amber-500 bg-amber-500/10 text-amber-400 font-bold"
                        : "border-slate-800 bg-slate-950/60 text-slate-300 hover:border-slate-700"
                    }`}
                  >
                    <div className="text-sm font-semibold">{b.label}</div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {step === 2 && (
            <div>
              <h3 className="mb-3 text-sm font-bold text-slate-200">
                2-Qadam: Qayerda ishlamoqchisiz?
              </h3>
              <div className="grid gap-3 sm:grid-cols-2">
                {LOCATIONS.map((l) => (
                  <button
                    key={l.id}
                    onClick={() => {
                      setLocation(l.id);
                      setStep(3);
                    }}
                    className={`rounded-xl border p-4 text-left transition-all ${
                      location === l.id
                        ? "border-amber-500 bg-amber-500/10 text-amber-400 font-bold"
                        : "border-slate-800 bg-slate-950/60 text-slate-300 hover:border-slate-700"
                    }`}
                  >
                    <div className="text-sm font-semibold">{l.label}</div>
                  </button>
                ))}
              </div>
              <button
                onClick={() => setStep(1)}
                className="mt-4 text-xs text-slate-400 hover:text-slate-200"
              >
                ← Orqaga
              </button>
            </div>
          )}

          {step === 3 && (
            <div>
              <h3 className="mb-3 text-sm font-bold text-slate-200">
                3-Qadam: Qaysi soha sizga yaqinroq?
              </h3>
              <div className="grid gap-3 sm:grid-cols-3">
                {SECTORS.map((sec) => (
                  <button
                    key={sec.id}
                    onClick={() => setSector(sec.id)}
                    className={`rounded-xl border p-4 text-left transition-all ${
                      sector === sec.id
                        ? "border-amber-500 bg-amber-500/10 text-amber-400 font-bold"
                        : "border-slate-800 bg-slate-950/60 text-slate-300 hover:border-slate-700"
                    }`}
                  >
                    <div className="text-sm font-semibold">{sec.label}</div>
                  </button>
                ))}
              </div>
              <div className="mt-6 flex items-center justify-between">
                <button
                  onClick={() => setStep(2)}
                  className="text-xs text-slate-400 hover:text-slate-200"
                >
                  ← Orqaga
                </button>
                <button
                  onClick={handleMatch}
                  disabled={loading}
                  className="rounded-xl bg-amber-500 px-6 py-2.5 font-bold text-slate-950 hover:bg-amber-400 shadow-lg shadow-amber-500/20 transition-all"
                >
                  {loading ? "Saralanmoqda…" : "Mos g‘oyalarni saralash"}
                </button>
              </div>
              {error && <p className="mt-3 text-xs text-red-400">{error}</p>}
            </div>
          )}
        </div>
      ) : (
        <div>
          <div className="mb-4 flex items-center justify-between border-b border-slate-800 pb-3">
            <h3 className="text-base font-bold text-amber-400">
              🎉 Siz Uylagan Parametrlarga Mos Top 3 G&apos;oya:
            </h3>
            <button
              onClick={handleReset}
              className="text-xs text-slate-400 hover:text-white underline"
            >
              🔄 Qayta tanlash
            </button>
          </div>

          <div className="space-y-3">
            {results.length > 0 ? (
              results.map((art) => (
                <div
                  key={art.id}
                  className="rounded-xl border border-slate-800 bg-slate-950/90 p-4 transition-all hover:border-amber-500/50"
                >
                  <div className="mb-1 flex items-center justify-between text-xs">
                    <span className="rounded-full bg-amber-500/10 px-2 py-0.5 font-semibold text-amber-400">
                      {art.category?.name || "Biznes G'oyasi"}
                    </span>
                    <span className="text-slate-400">Mezonlar bo‘yicha mos</span>
                  </div>
                  <h4 className="font-bold text-slate-100 text-sm mb-1">{art.title}</h4>
                  <p className="text-xs text-slate-300 line-clamp-2 mb-3">{art.summary}</p>
                  <Link
                    href={`/${art.category?.slug || "biznes-goyalari"}/${art.slug}`}
                    className="inline-block rounded-lg bg-amber-500/10 border border-amber-500/30 px-3 py-1.5 text-xs font-bold text-amber-400 hover:bg-amber-500 hover:text-slate-950 transition-colors"
                  >
                    G‘oyani batafsil ko‘rish →
                  </Link>
                </div>
              ))
            ) : (
              <p className="py-6 text-center text-xs text-slate-400">
                Ushbu filtrlarga mos keluvchi g&apos;oyalar topilmadi. Qayta urinib ko&apos;ring.
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

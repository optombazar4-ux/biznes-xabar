"use client";

import { useState } from "react";

export default function BusinessCalculator() {
  const [tab, setTab] = useState("margin");

  // Margin Calculator State
  const [salePrice, setSalePrice] = useState(100000);
  const [costPrice, setCostPrice] = useState(60000);
  const [deliveryCost, setDeliveryCost] = useState(5000);
  const [adCost, setAdCost] = useState(10000);

  // Break Even Calculator State
  const [fixedCosts, setFixedCosts] = useState(5000000); // Ijara, Oyliklar, Kommunal
  const [unitMargin, setUnitMargin] = useState(25000);

  // Calculations
  const totalCostPerUnit = Number(costPrice) + Number(deliveryCost) + Number(adCost);
  const netProfitPerUnit = Number(salePrice) - totalCostPerUnit;
  const marginPercent = salePrice > 0 ? ((netProfitPerUnit / salePrice) * 100).toFixed(1) : 0;
  const breakEvenUnits = unitMargin > 0 ? Math.ceil(Number(fixedCosts) / Number(unitMargin)) : 0;
  const breakEvenRevenue = breakEvenUnits * Number(salePrice);

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 shadow-2xl backdrop-blur-md">
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-4">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            🧮 Interaktiv Biznes Kalkulyatori
          </h2>
          <p className="text-xs text-slate-400">
            Foyda, marja va zararsizlik nuqtasini so&apos;mda darhol hisoblang
          </p>
        </div>

        <div className="flex gap-2">
          <button
            onClick={() => setTab("margin")}
            className={`rounded-lg px-3.5 py-1.5 text-xs font-semibold transition ${
              tab === "margin"
                ? "bg-amber-500 text-slate-950 font-bold"
                : "border border-slate-800 bg-slate-950 text-slate-300 hover:border-amber-500/50"
            }`}
          >
            📊 Marja va Sof Foyda
          </button>
          <button
            onClick={() => setTab("breakeven")}
            className={`rounded-lg px-3.5 py-1.5 text-xs font-semibold transition ${
              tab === "breakeven"
                ? "bg-amber-500 text-slate-950 font-bold"
                : "border border-slate-800 bg-slate-950 text-slate-300 hover:border-amber-500/50"
            }`}
          >
            🎯 Zararsizlik Nuqtasi (Break-Even)
          </button>
        </div>
      </div>

      {tab === "margin" ? (
        <div className="grid gap-6 md:grid-cols-2">
          <div className="space-y-4">
            <div>
              <label className="mb-1 block text-xs font-semibold text-slate-300">
                Sotish narxi (1 dona, so&apos;mda)
              </label>
              <input
                type="number"
                value={salePrice}
                onChange={(e) => setSalePrice(e.target.value)}
                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3.5 py-2 text-sm outline-none focus:border-amber-500 text-slate-100 font-mono"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-semibold text-slate-300">
                Xarid / Ishlab chiqarish tannarxi (so&apos;mda)
              </label>
              <input
                type="number"
                value={costPrice}
                onChange={(e) => setCostPrice(e.target.value)}
                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3.5 py-2 text-sm outline-none focus:border-amber-500 text-slate-100 font-mono"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-semibold text-slate-300">
                Qadoqlash va yetkazish xarajati (so&apos;mda)
              </label>
              <input
                type="number"
                value={deliveryCost}
                onChange={(e) => setDeliveryCost(e.target.value)}
                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3.5 py-2 text-sm outline-none focus:border-amber-500 text-slate-100 font-mono"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-semibold text-slate-300">
                1 dona mahsulotga reklama/marketing xarajati (Target/CAC)
              </label>
              <input
                type="number"
                value={adCost}
                onChange={(e) => setAdCost(e.target.value)}
                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3.5 py-2 text-sm outline-none focus:border-amber-500 text-slate-100 font-mono"
              />
            </div>
          </div>

          <div className="flex flex-col justify-between rounded-xl border border-slate-800 bg-slate-950/80 p-5">
            <div>
              <h3 className="mb-4 text-sm font-bold text-slate-200 uppercase tracking-wide">
                📈 Hisob-kitob Natijasi
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between border-b border-slate-800 pb-2 text-xs">
                  <span className="text-slate-400">Umumiy 1 dona xarajat:</span>
                  <span className="font-mono text-slate-200">{totalCostPerUnit.toLocaleString()} so&apos;m</span>
                </div>
                <div className="flex justify-between border-b border-slate-800 pb-2 text-sm">
                  <span className="text-slate-300">1 donadan Sof Foyda:</span>
                  <span className={`font-bold font-mono ${netProfitPerUnit >= 0 ? "text-emerald-400" : "text-red-400"}`}>
                    {netProfitPerUnit.toLocaleString()} so&apos;m
                  </span>
                </div>
                <div className="flex justify-between border-b border-slate-800 pb-2 text-sm">
                  <span className="text-slate-300">Sof Marja (Margin %):</span>
                  <span className={`font-bold font-mono ${marginPercent >= 20 ? "text-amber-400" : "text-yellow-500"}`}>
                    {marginPercent}%
                  </span>
                </div>
              </div>
            </div>

            <div className="mt-4 rounded-lg bg-slate-900 p-3 text-xs leading-relaxed text-slate-400 border border-slate-800">
              💡 <strong>Tavsiya:</strong> E-commerce va chakana savdoda 25% dan yuqori marja barqaror hisoblanadi.
            </div>
          </div>
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2">
          <div className="space-y-4">
            <div>
              <label className="mb-1 block text-xs font-semibold text-slate-300">
                Oylik Doimiy Xarajatlar (Ijara, Oyliklar, Kommunal, Aloqa)
              </label>
              <input
                type="number"
                value={fixedCosts}
                onChange={(e) => setFixedCosts(e.target.value)}
                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3.5 py-2 text-sm outline-none focus:border-amber-500 text-slate-100 font-mono"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-semibold text-slate-300">
                1 dona mahsulotdan qoladigan Sof Marja (Foyda, so&apos;mda)
              </label>
              <input
                type="number"
                value={unitMargin}
                onChange={(e) => setUnitMargin(e.target.value)}
                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3.5 py-2 text-sm outline-none focus:border-amber-500 text-slate-100 font-mono"
              />
            </div>
          </div>

          <div className="flex flex-col justify-between rounded-xl border border-slate-800 bg-slate-950/80 p-5">
            <div>
              <h3 className="mb-4 text-sm font-bold text-slate-200 uppercase tracking-wide">
                🎯 Zararsizlik Nuqtasi (Break-Even)
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between border-b border-slate-800 pb-2 text-sm">
                  <span className="text-slate-300">Oylik minimal sotish hajmi:</span>
                  <span className="font-bold font-mono text-amber-400">
                    {breakEvenUnits.toLocaleString()} dona / oy
                  </span>
                </div>
                <div className="flex justify-between border-b border-slate-800 pb-2 text-xs">
                  <span className="text-slate-400">Zararsizlik oylik tushumi:</span>
                  <span className="font-mono text-slate-200">
                    {breakEvenRevenue.toLocaleString()} so&apos;m
                  </span>
                </div>
              </div>
            </div>

            <div className="mt-4 rounded-lg bg-slate-900 p-3 text-xs leading-relaxed text-slate-400 border border-slate-800">
              🎯 Zararsizlik nuqtasidan keyin sotilgan har bir dona mahsulot biznesingiz uchun <strong>100% sof foyda</strong> keltiradi!
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

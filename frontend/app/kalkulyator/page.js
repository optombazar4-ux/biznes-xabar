import BusinessCalculator from "../../components/BusinessCalculator";

export const metadata = {
  title: "Biznes Kalkulyatori — Tannarx, Marja va Zararsizlik Nuqtasi Hisoblagich",
  description:
    "O'zbekistonda tadbirkorlar va startaplar uchun bepul interaktiv biznes kalkulyatori: unit economics, marja foizi va break-even zararsizlik hajmini so'mda hisoblang.",
  alternates: { canonical: "/kalkulyator" },
};

export default function CalculatorPage() {
  return (
    <div className="mx-auto max-w-4xl py-10">
      <div className="mb-8">
        <p className="mb-1 text-sm font-semibold uppercase tracking-wide text-amber-400">
          🛠 Amaliy Instrument
        </p>
        <h1 className="text-3xl font-bold leading-tight">
          Tadbirkorlar uchun Interaktiv Biznes Kalkulyatori
        </h1>
        <p className="mt-2 text-slate-300">
          Mahsulot yoki xizmatingiz sotish narxi, xarajatlari hamda zararsizlik nuqtasini sekundlarda ancha aniq hisoblang.
        </p>
      </div>

      <BusinessCalculator />
    </div>
  );
}

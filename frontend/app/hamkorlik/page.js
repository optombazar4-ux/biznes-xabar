import Link from "next/link";

export const metadata = {
  title: "Hamkorlik va B2B Reklama — Media Kit",
  description:
    "Biznes Darslari platformasi bilan B2B hamkorlik: Banklar, to'lov tizimlari (Click, Payme, Uzum), CRM va SaaS vositalari uchun maqsadli auditoriya va sponsorlik paketlari.",
  alternates: { canonical: "/hamkorlik" },
};

const STATS = [
  { value: "113+", label: "Amaliy biznes darslari" },
  { value: "75+", label: "Verifikatsiya qilingan biznes g'oyalari" },
  { value: "100%", label: "O'zbek tilidagi amaliy kontent" },
  { value: "1.2M+", label: "O'zbekistondagi Kichik biznes TAM" },
];

const PACKAGES = [
  {
    title: "Soha / Bo'lim Homiyligi",
    price: "Kelishuv asosida",
    features: [
      "Muayyan bo'limda (masalan, Moliya yoki Onlayn Biznes) brend banneri",
      "Darslar ichida 'Tavsiya etilgan integratsiya / vosita' belgisi",
      "Telegram kanalda haftalik alohida sharh (Review)",
    ],
    recommended: true,
  },
  {
    title: "Lead Generation & B2B Integratsiya",
    price: "Pay-per-lead / Natija",
    features: [
      "Bank hisobraqami, Payme/Click yechimi yoki CRMga qiziqqan tadbirkorlar leadi",
      "Kalkulyatorlar ichida hisob-kitob asosida xizmatni tavsiya qilish",
      "Direct API / Form integratsiyasi",
    ],
    recommended: false,
  },
  {
    title: "Ekspertizaga Asoslangan Maqola",
    price: "Bir martalik",
    features: [
      "Tahririyatimiz ekspertlari bilan birga tayyorlangan amaliy keys (Case Study)",
      "SEO doimiy indeksatsiyasi va SEO Intent Landing Page'ga ulash",
      "Telegram va ijtimoiy tarmoqlarda ulashish",
    ],
    recommended: false,
  },
];

export default function PartnershipPage() {
  return (
    <div className="mx-auto max-w-4xl py-10">
      <div className="mb-10 text-center">
        <span className="inline-block rounded-full bg-amber-500/10 px-3.5 py-1 text-xs font-bold uppercase tracking-wider text-amber-400 border border-amber-500/20 mb-3">
          🤝 B2B Hamkorlik & Media Kit
        </span>
        <h1 className="text-3xl font-bold leading-tight sm:text-4xl text-slate-100">
          O&apos;zbekiston Tadbirkorlariga O&apos;z Xizmatlaringizni Eling
        </h1>
        <p className="mx-auto mt-3 max-w-2xl text-slate-300 text-sm sm:text-base leading-relaxed">
          Biznes Darslari — yangi va faoliyat yuritayotgan tadbirkorlar uchun o&apos;zbek tilidagi amaliy bilimlar va vositalar bazasi.
        </p>
      </div>

      {/* Metrics */}
      <div className="mb-12 grid grid-cols-2 gap-4 sm:grid-cols-4">
        {STATS.map((s) => (
          <div key={s.label} className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 text-center backdrop-blur-md">
            <div className="text-3xl font-bold text-amber-400 font-mono">{s.value}</div>
            <div className="mt-1 text-xs text-slate-400">{s.label}</div>
          </div>
        ))}
      </div>

      {/* Packages */}
      <h2 className="mb-6 text-2xl font-bold text-slate-100 text-center sm:text-left">
        💼 Hamkorlik Paketlari
      </h2>
      <div className="mb-12 grid gap-6 md:grid-cols-3">
        {PACKAGES.map((pkg) => (
          <div
            key={pkg.title}
            className={`flex flex-col justify-between rounded-2xl border p-6 backdrop-blur-md transition-all ${
              pkg.recommended
                ? "border-amber-500 bg-slate-900/90 shadow-xl shadow-amber-500/10"
                : "border-slate-800 bg-slate-900/40"
            }`}
          >
            <div>
              {pkg.recommended && (
                <span className="mb-3 inline-block rounded-full bg-amber-500 text-slate-950 px-2.5 py-0.5 text-xs font-bold">
                  ⭐ Eng Mashhur
                </span>
              )}
              <h3 className="text-lg font-bold text-slate-100 mb-2">{pkg.title}</h3>
              <div className="text-sm font-bold text-amber-400 mb-4">{pkg.price}</div>
              <ul className="space-y-2.5 text-xs text-slate-300">
                {pkg.features.map((f, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="text-amber-400 font-bold">✓</span>
                    <span>{f}</span>
                  </li>
                ))}
              </ul>
            </div>

            <a
              href="mailto:hamkorlik@biznesdarslari.uz"
              className={`mt-6 block rounded-xl py-2.5 text-center text-xs font-bold transition-all ${
                pkg.recommended
                  ? "bg-amber-500 text-slate-950 hover:bg-amber-400"
                  : "border border-slate-700 bg-slate-950 text-slate-200 hover:border-amber-500"
              }`}
            >
              Murojaat qilish →
            </a>
          </div>
        ))}
      </div>

      {/* Contact Banner */}
      <div className="rounded-2xl border border-slate-800 bg-gradient-to-r from-amber-950/40 via-slate-900 to-slate-950 p-8 text-center sm:text-left flex flex-wrap items-center justify-between gap-6">
        <div>
          <h3 className="text-xl font-bold text-slate-100">Maxsus Taklifingiz Bormi?</h3>
          <p className="text-xs text-slate-300 mt-1 max-w-md">
            Bank, to&apos;lov tizimi, CRM yoki SaaS mahsulotingiz uchun maxsus Lead Generation kampaniyasini rejalashtiraylik.
          </p>
        </div>
        <a
          href="mailto:hamkorlik@biznesdarslari.uz"
          className="rounded-xl bg-amber-500 px-6 py-3 text-sm font-bold text-slate-950 hover:bg-amber-400 transition-all shadow-lg shadow-amber-500/20"
        >
          📧 hamkorlik@biznesdarslari.uz
        </a>
      </div>
    </div>
  );
}

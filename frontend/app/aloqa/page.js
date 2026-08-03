export const metadata = {
  title: "Aloqa",
  description:
    "Biznes Darslari jamoasi va tahririyati bilan bog'lanish: takliflar, tahririyat, ekspertlar va hamkorlik bo'yicha murojaatlar.",
  alternates: { canonical: "/aloqa" },
};

const CONTACTS = [
  {
    icon: "📢",
    title: "Telegram kanal",
    value: "@biznesxabari",
    href: "https://t.me/biznesxabari",
    note: "Rasmiy darslar va e'lonlar",
  },
  {
    icon: "🤝",
    title: "Hamkorlik va Reklama",
    value: "hamkorlik@biznesdarslari.uz",
    href: "mailto:hamkorlik@biznesdarslari.uz",
    note: "B2B hamkorlik va takliflar",
  },
  {
    icon: "✉️",
    title: "Tahririyat va Takliflar",
    value: "salom@biznesdarslari.uz",
    href: "mailto:salom@biznesdarslari.uz",
    note: "Umumiy murojaat va fikrlar",
  },
  {
    icon: "🛡️",
    title: "Ekspertlar va Fikr-mulohaza",
    value: "tahririyat@biznesdarslari.uz",
    href: "mailto:tahririyat@biznesdarslari.uz",
    note: "Darslar tahririyati va manbalar",
  },
];

export default function ContactPage() {
  return (
    <div className="mx-auto max-w-3xl py-10">
      <h1 className="mb-3 text-3xl font-bold">Aloqa</h1>
      <p className="mb-8 leading-relaxed text-slate-300">
        Taklifingiz bormi, maqolada xatolik topdingizmi yoki hamkorlik qilmoqchimisiz?
        Quyidagi rasmiy kanallar orqali murojaat qiling — tahririyatimiz 1-2 ish kuni ichida javob beradi.
      </p>

      <div className="grid gap-4 sm:grid-cols-2">
        {CONTACTS.map((c) => (
          <a
            key={c.title}
            href={c.href}
            target={c.href.startsWith("http") ? "_blank" : undefined}
            rel={c.href.startsWith("http") ? "noopener noreferrer" : undefined}
            className="rounded-xl border border-slate-800 bg-slate-900/50 p-5 transition-colors hover:border-amber-500"
          >
            <div className="mb-2 text-2xl">{c.icon}</div>
            <div className="font-bold text-white">{c.title}</div>
            <div className="text-sky-400 font-mono text-sm">{c.value}</div>
            <div className="mt-1 text-xs text-slate-400">{c.note}</div>
          </a>
        ))}
      </div>

      <div className="mt-8 rounded-xl border border-amber-500/20 bg-amber-500/5 p-5 text-sm leading-relaxed text-slate-300">
        <strong className="text-amber-400">Xatolik topdingizmi?</strong> Maqoladagi noaniqlik
        yoki qonunchilikdagi yangilanishlar bo&apos;yicha yozsangiz, tahririyatimiz ekspertlari tekshirib darhol tuzatadilar.
      </div>
    </div>
  );
}

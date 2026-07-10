export const metadata = {
  title: "Biz haqimizda",
  description:
    "Biznes Darslari — O'zbekistonda biznes ochish va yuritishni o'rgatuvchi platforma. Darslar qanday tayyorlanishi haqida.",
  alternates: { canonical: "/haqida" },
};

export default function AboutPage() {
  return (
    <div className="mx-auto max-w-3xl py-10">
      <h1 className="mb-6 text-3xl font-bold">Biz haqimizda</h1>

      <div className="space-y-5 leading-relaxed text-slate-300">
        <p>
          <strong className="text-white">Biznes Darslari</strong> (biznesxabar.uz) —
          O&apos;zbekistonda biznes ochish va yuritishni o&apos;rgatuvchi ta&apos;lim
          platformasi. Maqsadimiz — o&apos;zbek tadbirkorlariga biznesni boshlash, moliyani
          boshqarish, marketing, sotuv va o&apos;sish bo&apos;yicha amaliy, tushunarli darslar
          berish.
        </p>

        <h2 className="pt-2 text-xl font-bold text-white">Darslar qanday tayyorlanadi</h2>
        <p>
          Har bir dars jahon miqyosida isbotlangan eng yaxshi biznes amaliyotlariga (best
          practices) asoslanadi, LEKIN <strong className="text-white">O&apos;zbekiston
          sharoitiga moslashtiriladi</strong>: mahalliy ro&apos;yxatdan o&apos;tish (YaTT/MChJ),
          O&apos;zbekiston soliqlari, Payme/Click/Uzum kabi mahalliy tizimlar, so&apos;mdagi
          realistik misollar. Bu shunchaki tarjima emas — o&apos;zbek tadbirkori ertaga
          qo&apos;llay oladigan amaliy bilim.
        </p>
        <p>
          Darslar <strong className="text-white">eskirmaydi (evergreen)</strong>: bir marta
          tayyorlangan sifatli dars yillar davomida foydali bo&apos;lib qoladi. Mavzular
          biznesni boshlashdan tortib masshtablashgacha bo&apos;lgan yo&apos;lni qamrab oladi.
        </p>

        <h2 className="pt-2 text-xl font-bold text-white">Nima uchun bepul</h2>
        <p>
          Biznes Darslari — ochiq platforma. Barcha darslar bepul, sayt reklama va homiylik
          hisobidan rivojlantiriladi. Yangi darslardan birinchilardan bo&apos;lib xabar topish
          uchun{" "}
          <a
            href="https://t.me/biznesxabari"
            target="_blank"
            rel="noopener noreferrer"
            className="text-sky-400 hover:underline"
          >
            Telegram kanalimizga
          </a>{" "}
          obuna bo&apos;ling.
        </p>

        <h2 className="pt-2 text-xl font-bold text-white">Bog&apos;lanish</h2>
        <p>
          Takliflar, xatolar haqida xabar yoki hamkorlik bo&apos;yicha{" "}
          <a href="/aloqa" className="text-sky-400 hover:underline">
            Aloqa sahifasi
          </a>{" "}
          orqali murojaat qiling.
        </p>
      </div>
    </div>
  );
}

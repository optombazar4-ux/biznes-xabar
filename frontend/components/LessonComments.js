"use client";

import { useEffect, useState } from "react";

export default function LessonComments({ articleSlug }) {
  const [comments, setComments] = useState([]);
  const [author, setAuthor] = useState("");
  const [content, setContent] = useState("");
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    const key = `comments_${articleSlug}`;
    const saved = localStorage.getItem(key);

    const initialDefault = [
      {
        id: "c1",
        author: "Javohir (Tadbirkor)",
        date: "Bugun, 14:20",
        content: "Juda amaliy va kerakli darslik bo'libdi! Ayniqsa boshlang'ich kapital va 7 kunlik test rejasi bo'yicha berilgan maslahatlar juda foydali.",
        likes: 8,
      },
      {
        id: "c2",
        author: "Aziza (SMM Mutaxassisi)",
        date: "Kecha, 18:45",
        content: "Ushbu yo'nalish bo'yicha birinchi 3 ta mijozni jalb qilishdagi Telegram kanallar strategiyasi to'g'ri ko'rsatilgan. Rahmat!",
        likes: 5,
      },
    ];

    if (saved) {
      try {
        setComments(JSON.parse(saved));
      } catch {
        setComments(initialDefault);
      }
    } else {
      setComments(initialDefault);
    }
  }, [articleSlug]);

  function handleSubmit(e) {
    e.preventDefault();
    if (!author.trim() || !content.trim()) return;

    const newComment = {
      id: Date.now().toString(),
      author: author.trim(),
      date: "Hozirgina",
      content: content.trim(),
      likes: 1,
    };

    const updated = [newComment, ...comments];
    setComments(updated);
    localStorage.setItem(`comments_${articleSlug}`, JSON.stringify(updated));

    setContent("");
    setSubmitted(true);
    setTimeout(() => setSubmitted(false), 3000);
  }

  function handleLike(id) {
    const updated = comments.map((c) =>
      c.id === id ? { ...c, likes: c.likes + 1 } : c
    );
    setComments(updated);
    localStorage.setItem(`comments_${articleSlug}`, JSON.stringify(updated));
  }

  return (
    <section className="mt-10 border-t border-slate-800 pt-8">
      <div className="mb-6 flex items-center justify-between">
        <h3 className="text-xl font-bold text-slate-100 flex items-center gap-2">
          💬 Muhokama va Izohlar ({comments.length})
        </h3>
        <span className="text-xs text-slate-400">Tadbirkorlar tajribasi</span>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="mb-8 rounded-xl border border-slate-800 bg-slate-900/60 p-5 backdrop-blur-md">
        <div className="mb-4">
          <label className="mb-1 block text-xs font-semibold text-slate-300">
            Ismingiz va faoliyat yo&apos;nalishingiz
          </label>
          <input
            type="text"
            value={author}
            onChange={(e) => setAuthor(e.target.value)}
            placeholder="Masalan: Sardor (Yangi tadbirkor)"
            className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3.5 py-2 text-sm text-slate-100 outline-none focus:border-amber-500"
            required
          />
        </div>

        <div className="mb-4">
          <label className="mb-1 block text-xs font-semibold text-slate-300">
            Fikringiz, tajribangiz yoki savolingiz
          </label>
          <textarea
            rows={3}
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Ushbu dars bo'yicha o'z fikringiz yoki tajribangizni yozing..."
            className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3.5 py-2 text-sm text-slate-100 outline-none focus:border-amber-500 resize-none"
            required
          />
        </div>

        {submitted && (
          <div className="mb-3 text-xs text-emerald-400 font-semibold">
            ✅ Izohingiz muvaffaqiyatli chop etildi!
          </div>
        )}

        <button
          type="submit"
          className="rounded-lg bg-amber-500 px-5 py-2.5 text-xs font-bold text-slate-950 hover:bg-amber-400 transition-all shadow-lg shadow-amber-500/10"
        >
          💬 Izoh Qoldirish
        </button>
      </form>

      {/* List */}
      <div className="space-y-4">
        {comments.map((c) => (
          <div key={c.id} className="rounded-xl border border-slate-800 bg-slate-950/70 p-4 transition-colors hover:border-slate-700">
            <div className="mb-2 flex items-center justify-between text-xs">
              <span className="font-bold text-amber-400">{c.author}</span>
              <span className="text-slate-500">{c.date}</span>
            </div>
            <p className="mb-3 text-sm leading-relaxed text-slate-200">{c.content}</p>
            <button
              onClick={() => handleLike(c.id)}
              className="flex items-center gap-1 text-xs text-slate-400 hover:text-amber-400 transition-colors"
            >
              <span>👍 Foydali</span>
              <span className="rounded-full bg-slate-800 px-2 py-0.5 font-mono text-[10px] text-slate-300">
                {c.likes}
              </span>
            </button>
          </div>
        ))}
      </div>
    </section>
  );
}

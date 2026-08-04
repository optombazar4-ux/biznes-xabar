"use client";

import { useEffect, useState } from "react";

export default function LessonComments({ articleSlug }) {
  const storageKey = `lesson_notes_${articleSlug}`;
  const [notes, setNotes] = useState([]);
  const [content, setContent] = useState("");
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    try {
      setNotes(JSON.parse(localStorage.getItem(storageKey) || "[]"));
    } catch {
      setNotes([]);
    }
  }, [storageKey]);

  function handleSubmit(event) {
    event.preventDefault();
    const text = content.trim();
    if (!text) return;

    const updated = [
      { id: Date.now().toString(), content: text, createdAt: new Date().toISOString() },
      ...notes,
    ];
    setNotes(updated);
    localStorage.setItem(storageKey, JSON.stringify(updated));
    setContent("");
    setSaved(true);
    window.setTimeout(() => setSaved(false), 2500);
  }

  function removeNote(id) {
    const updated = notes.filter((note) => note.id !== id);
    setNotes(updated);
    localStorage.setItem(storageKey, JSON.stringify(updated));
  }

  return (
    <section className="mt-10 border-t border-slate-800 pt-8">
      <h3 className="text-xl font-bold text-slate-100">📝 Shaxsiy qaydlar</h3>
      <p className="mb-5 mt-1 text-xs text-slate-400">
        Qaydlar faqat shu brauzerda saqlanadi; ular ommaga chop etilmaydi va serverga yuborilmaydi.
      </p>

      <form onSubmit={handleSubmit} className="mb-6 rounded-xl border border-slate-800 bg-slate-900/60 p-5">
        <textarea
          rows={3}
          value={content}
          onChange={(event) => setContent(event.target.value)}
          placeholder="Dars bo‘yicha fikr yoki keyingi qadamingizni yozing…"
          className="mb-3 w-full resize-none rounded-lg border border-slate-700 bg-slate-950 px-3.5 py-2 text-sm outline-none focus:border-amber-500"
          required
        />
        {saved && <p className="mb-3 text-xs font-semibold text-emerald-400">✅ Qayd brauzeringizda saqlandi</p>}
        <button className="rounded-lg bg-amber-500 px-5 py-2.5 text-xs font-bold text-slate-950 hover:bg-amber-400">
          Qaydni saqlash
        </button>
      </form>

      <div className="space-y-3">
        {notes.map((note) => (
          <div key={note.id} className="rounded-xl border border-slate-800 bg-slate-950/70 p-4">
            <p className="whitespace-pre-wrap text-sm text-slate-200">{note.content}</p>
            <div className="mt-3 flex items-center justify-between text-xs text-slate-500">
              <time dateTime={note.createdAt}>{new Date(note.createdAt).toLocaleDateString("uz-UZ")}</time>
              <button onClick={() => removeNote(note.id)} className="hover:text-red-400">O‘chirish</button>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

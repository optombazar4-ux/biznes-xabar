"use client";

import { useState } from "react";

export default function LessonQuiz({ quiz }) {
  const [userAnswers, setUserAnswers] = useState({});
  const [submitted, setSubmitted] = useState(false);

  if (!quiz || !Array.isArray(quiz) || quiz.length === 0) {
    return null;
  }

  const handleSelect = (qIndex, optionIndex) => {
    if (submitted) return;
    setUserAnswers((prev) => ({
      ...prev,
      [qIndex]: optionIndex,
    }));
  };

  const calculateScore = () => {
    let score = 0;
    quiz.forEach((q, idx) => {
      if (userAnswers[idx] === q.answer_index) {
        score += 1;
      }
    });
    return score;
  };

  const score = calculateScore();
  const allAnswered = Object.keys(userAnswers).length === quiz.length;

  return (
    <div className="mb-8 rounded-2xl border border-slate-800 bg-slate-900/80 p-6 shadow-xl">
      <div className="mb-4 flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <span className="text-2xl">🧠</span>
          <h3 className="text-xl font-bold text-slate-100">Bilimingizni sinang (Quiz)</h3>
        </div>
        <span className="rounded-full bg-amber-500/10 px-3 py-1 text-xs font-semibold text-amber-400">
          {quiz.length} ta savol
        </span>
      </div>

      <div className="space-y-6">
        {quiz.map((q, qIdx) => {
          const selected = userAnswers[qIdx];
          const isCorrect = selected === q.answer_index;

          return (
            <div key={qIdx} className="rounded-xl border border-slate-800/80 bg-slate-950/60 p-4">
              <p className="mb-3 font-semibold text-slate-200">
                {qIdx + 1}. {q.question}
              </p>

              <div className="grid gap-2 sm:grid-cols-2">
                {(q.options || []).map((opt, optIdx) => {
                  let btnStyle =
                    "border-slate-800 bg-slate-900 text-slate-300 hover:border-amber-500/50 hover:bg-slate-800";

                  if (selected === optIdx) {
                    btnStyle = "border-amber-500 bg-amber-500/20 text-amber-300 font-semibold";
                  }

                  if (submitted) {
                    if (optIdx === q.answer_index) {
                      btnStyle = "border-emerald-500 bg-emerald-500/20 text-emerald-300 font-bold";
                    } else if (selected === optIdx) {
                      btnStyle = "border-rose-500 bg-rose-500/20 text-rose-300 font-semibold";
                    } else {
                      btnStyle = "border-slate-800/50 bg-slate-900/40 text-slate-500 opacity-60";
                    }
                  }

                  return (
                    <button
                      key={optIdx}
                      disabled={submitted}
                      onClick={() => handleSelect(qIdx, optIdx)}
                      className={`flex items-center gap-3 rounded-lg border p-3 text-left text-sm transition ${btnStyle}`}
                    >
                      <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full border border-current text-xs font-bold">
                        {String.fromCharCode(65 + optIdx)}
                      </span>
                      <span>{opt}</span>
                    </button>
                  );
                })}
              </div>

              {submitted && (
                <div
                  className={`mt-3 rounded-lg p-3 text-xs leading-relaxed ${
                    isCorrect
                      ? "border border-emerald-800/50 bg-emerald-950/30 text-emerald-300"
                      : "border border-rose-800/50 bg-rose-950/30 text-rose-300"
                  }`}
                >
                  <strong>{isCorrect ? "✅ To'g'ri!" : "❌ Noto'g'ri."}</strong> {q.explanation}
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div className="mt-6 flex flex-wrap items-center justify-between gap-4 border-t border-slate-800 pt-4">
        {!submitted ? (
          <button
            disabled={!allAnswered}
            onClick={() => setSubmitted(true)}
            className={`rounded-xl px-6 py-2.5 font-bold transition ${
              allAnswered
                ? "bg-amber-500 text-slate-950 hover:bg-amber-400"
                : "cursor-not-allowed bg-slate-800 text-slate-500"
            }`}
          >
            Javoblarni tekshirish
          </button>
        ) : (
          <div className="flex w-full flex-wrap items-center justify-between gap-3">
            <div className="text-sm font-semibold text-slate-200">
              Natijangiz: <span className="text-amber-400">{score}</span> / {quiz.length}
              {score === quiz.length && " 🏆 A'lo natija!"}
              {score > 0 && score < quiz.length && " 👍 Yaxshi, takrorlab turing!"}
              {score === 0 && " 📚 Darsni qayta o'qib chiqishni tavsiya etamiz."}
            </div>
            <button
              onClick={() => {
                setSubmitted(false);
                setUserAnswers({});
              }}
              className="rounded-lg border border-slate-700 px-4 py-1.5 text-xs text-slate-300 hover:border-amber-500 hover:text-white"
            >
              🔄 Qayta topshirish
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

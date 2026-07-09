// Yengil markdown renderer — AI yaratadigan kontent uchun yetarli:
// ## / ### sarlavhalar, - / * ro'yxatlar, **qalin** matn, oddiy paragraflar.
// Tashqi kutubxonasiz (server komponentida ishlaydi).

function renderInline(text, keyPrefix) {
  // **qalin** matnni <strong> ga aylantiradi
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return (
        <strong key={`${keyPrefix}-${i}`} className="font-semibold text-white">
          {part.slice(2, -2)}
        </strong>
      );
    }
    return part;
  });
}

export default function MarkdownContent({ content }) {
  const lines = (content || "").split("\n");
  const blocks = [];
  let list = null; // yig'ilayotgan ro'yxat elementlari
  let para = []; // yig'ilayotgan paragraf qatorlari

  const flushPara = () => {
    if (para.length) {
      blocks.push({ type: "p", text: para.join(" ") });
      para = [];
    }
  };
  const flushList = () => {
    if (list) {
      blocks.push({ type: "ul", items: list });
      list = null;
    }
  };

  for (const raw of lines) {
    const line = raw.trim();
    if (!line) {
      flushPara();
      flushList();
      continue;
    }
    if (line.startsWith("### ")) {
      flushPara();
      flushList();
      blocks.push({ type: "h3", text: line.slice(4) });
    } else if (line.startsWith("## ")) {
      flushPara();
      flushList();
      blocks.push({ type: "h2", text: line.slice(3) });
    } else if (line.startsWith("# ")) {
      flushPara();
      flushList();
      blocks.push({ type: "h2", text: line.slice(2) });
    } else if (/^[-*]\s+/.test(line)) {
      flushPara();
      (list ??= []).push(line.replace(/^[-*]\s+/, ""));
    } else {
      flushList();
      para.push(line);
    }
  }
  flushPara();
  flushList();

  return (
    <div className="space-y-4 leading-relaxed text-slate-300">
      {blocks.map((b, i) => {
        if (b.type === "h2") {
          return (
            <h2 key={i} className="mt-6 text-xl font-bold text-white">
              {renderInline(b.text, `h2-${i}`)}
            </h2>
          );
        }
        if (b.type === "h3") {
          return (
            <h3 key={i} className="mt-4 text-lg font-semibold text-white">
              {renderInline(b.text, `h3-${i}`)}
            </h3>
          );
        }
        if (b.type === "ul") {
          return (
            <ul key={i} className="list-disc space-y-1.5 pl-6">
              {b.items.map((it, j) => (
                <li key={j}>{renderInline(it, `li-${i}-${j}`)}</li>
              ))}
            </ul>
          );
        }
        return <p key={i}>{renderInline(b.text, `p-${i}`)}</p>;
      })}
    </div>
  );
}

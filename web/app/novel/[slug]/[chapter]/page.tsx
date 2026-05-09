import { notFound } from "next/navigation";
import { Deckle } from "@/components/Deckle";
import { Fleuron } from "@/components/Fleuron";
import { Gloss } from "@/components/Gloss";
import { Pagination } from "@/components/Pagination";
import { fetchChapter, type GlossaryEntry } from "@/lib/api";

const NUMBER_WORDS = [
  "Zero", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
  "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
  "Seventeen", "Eighteen", "Nineteen", "Twenty",
];
const TENS = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"];

function numberToWord(n: number): string {
  if (n < 0) return String(n);
  if (n <= 20) return NUMBER_WORDS[n];
  if (n < 100) {
    const t = Math.floor(n / 10);
    const r = n % 10;
    return r === 0 ? TENS[t] : `${TENS[t]}-${NUMBER_WORDS[r]}`;
  }
  return String(n);
}

function renderBody(body: string, glossary: GlossaryEntry[]) {
  const paragraphs = body.split(/\n\n+/);
  const byTerm = new Map<string, GlossaryEntry>();
  for (const g of glossary) {
    byTerm.set(g.translation, g);
    byTerm.set(g.term, g);
  }
  const terms = [...byTerm.keys()].sort((a, b) => b.length - a.length);

  return paragraphs.map((para, pi) => {
    if (terms.length === 0) {
      return <p key={pi}>{para}</p>;
    }
    const escaped = terms.map((t) => t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));
    const re = new RegExp(`(${escaped.join("|")})`, "g");
    const parts = para.split(re);
    return (
      <p key={pi}>
        {parts.map((part, i) => {
          const entry = byTerm.get(part);
          if (entry && i % 2 === 1) {
            return <Gloss key={i} term={part} entry={entry} />;
          }
          return <span key={i}>{part}</span>;
        })}
      </p>
    );
  });
}

export default async function ChapterPage(
  props: PageProps<"/novel/[slug]/[chapter]">,
) {
  const { slug, chapter } = await props.params;
  const number = Number(chapter);
  if (!Number.isFinite(number)) notFound();

  const ch = await fetchChapter(slug, number);
  if (!ch) notFound();

  return (
    <section className="chapter-shell" aria-label={`Chapter ${ch.number}`}>
      <div className="reading-ribbon" aria-hidden="true" />

      <article className="chapter">
        <Deckle />

        <p className="chapter__eyebrow">Chapter {numberToWord(ch.number)}</p>
        <h1 className="chapter__title">
          <em>{ch.name ?? `Chapter ${ch.number}`}</em>
        </h1>

        <div className="chapter__body">
          {renderBody(ch.body, ch.glossary)}
          <Fleuron variant="end" />
        </div>
      </article>

      <Pagination slug={slug} prev={ch.prev} next={ch.next} />
    </section>
  );
}

import type { GlossEntry } from "@/lib/mock";

export function Gloss({
  term,
  entry,
}: {
  term: string;
  entry: GlossEntry;
}) {
  return (
    <span className="gloss" tabIndex={0}>
      {term}
      <span className="gloss__card" role="tooltip">
        <span className="gloss__source">{entry.source}</span>
        <span className="gloss__pref">{entry.preferred}</span>
        <span className="gloss__meta">
          first canonized in chapter {entry.firstChapter}.
        </span>
        <span className="gloss__tag">{entry.tag}</span>
      </span>
    </span>
  );
}

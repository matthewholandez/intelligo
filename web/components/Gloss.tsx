import type { GlossaryEntry } from "@/lib/api";

export function Gloss({
  term,
  entry,
}: {
  term: string;
  entry: GlossaryEntry;
}) {
  return (
    <span className="gloss" tabIndex={0}>
      {term}
      <span className="gloss__card" role="tooltip">
        <span className="gloss__source">{entry.term}</span>
        <span className="gloss__pref">{entry.translation}</span>
        {entry.tag ? <span className="gloss__tag">{entry.tag}</span> : null}
      </span>
    </span>
  );
}

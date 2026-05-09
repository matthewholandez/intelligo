import type { TermRow } from "@/lib/api";

export function TermCard({ term }: { term: TermRow }) {
  return (
    <article className="term">
      <div className="term__rule">{term.source}</div>
      <div className="term__pref">{term.preferred}</div>
      {term.tag ? <span className="term__tag">{term.tag}</span> : null}
      <span className="term__ch">ch. {term.chapter}</span>
    </article>
  );
}

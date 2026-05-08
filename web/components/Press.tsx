import { press } from "@/lib/mock";

export function Press() {
  return (
    <div className="press" aria-label="Chapters being translated">
      {press.map((row, i) => (
        <div key={i} className="press__row">
          <div>
            <p className="press__title">
              <em>{row.novel}</em> · Chapter {row.chapter}
            </p>
            <p className="press__status">{row.status}</p>
          </div>
          <div className="press__bar" role="progressbar" aria-label="In progress" />
          <div className="press__attempt">
            attempt {row.attempt} of {row.attemptOf}
          </div>
        </div>
      ))}
    </div>
  );
}

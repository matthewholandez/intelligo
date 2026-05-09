import Link from "next/link";
import type { RecentChapter } from "@/lib/api";

export function ChapterCard({ item }: { item: RecentChapter }) {
  return (
    <Link
      href={`/novel/${item.novelSlug}/${item.chapter}`}
      className="card"
      aria-label={`${item.novel}${item.title ? ` — ${item.title}` : ""}`}
    >
      <div className="card__novel">
        <em>{item.novel}</em>
      </div>
      <h4 className="card__title">{item.title ?? `Chapter ${item.chapter}`}</h4>
      <p className="card__preview">{item.preview}</p>
      <span className="card__chapter">ch. {item.chapter}</span>
    </Link>
  );
}

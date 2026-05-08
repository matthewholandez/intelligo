import Link from "next/link";

type ChapterRef = { number: number; title: string };

export function Pagination({
  slug,
  prev,
  next,
}: {
  slug: string;
  prev: ChapterRef;
  next: ChapterRef;
}) {
  return (
    <nav className="pagination">
      <Link href={`/novel/${slug}/${prev.number}`}>
        ‹ Chapter {prev.number} · {prev.title}
      </Link>
      <span className="pagination__between">❦</span>
      <Link href={`/novel/${slug}/${next.number}`}>
        Chapter {next.number} · {next.title} ›
      </Link>
    </nav>
  );
}

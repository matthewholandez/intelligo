import Link from "next/link";
import type { ChapterRef } from "@/lib/api";

export function Pagination({
  slug,
  prev,
  next,
}: {
  slug: string;
  prev: ChapterRef | null;
  next: ChapterRef | null;
}) {
  return (
    <nav className="pagination">
      {prev ? (
        <Link href={`/novel/${slug}/${prev.number}`}>
          ‹ Chapter {prev.number}
          {prev.name ? ` · ${prev.name}` : ""}
        </Link>
      ) : (
        <span />
      )}
      <span className="pagination__between">❦</span>
      {next ? (
        <Link href={`/novel/${slug}/${next.number}`}>
          Chapter {next.number}
          {next.name ? ` · ${next.name}` : ""} ›
        </Link>
      ) : (
        <span />
      )}
    </nav>
  );
}

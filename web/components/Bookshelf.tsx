import Link from "next/link";
import { shelf } from "@/lib/mock";

export function Bookshelf() {
  return (
    <aside className="bookshelf" aria-label="Your shelf">
      <div className="bookshelf__mark">INTELLIGO</div>
      {shelf.map((novel) => {
        const cls = [
          "spine",
          novel.current ? "spine--current" : "",
          novel.spineWidth === "thin" ? "spine--thin" : "",
          novel.spineWidth === "wide" ? "spine--wide" : "",
        ]
          .filter(Boolean)
          .join(" ");
        const href = novel.current
          ? `/novel/${novel.slug}/23`
          : `/novel/${novel.slug}/1`;
        return (
          <Link
            key={novel.slug}
            href={href}
            className={cls}
            aria-current={novel.current ? "true" : undefined}
          >
            {novel.title}
          </Link>
        );
      })}
      <button className="bookshelf__add" aria-label="Add a volume" type="button">
        +
      </button>
    </aside>
  );
}

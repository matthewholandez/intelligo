import Link from "next/link";
import { fetchNovels, type Novel } from "@/lib/api";

async function loadNovels(): Promise<Novel[]> {
  try {
    return await fetchNovels();
  } catch {
    return [];
  }
}

export async function Bookshelf() {
  const novels = await loadNovels();
  return (
    <aside className="bookshelf" aria-label="Your shelf">
      <div className="bookshelf__mark">INTELLIGO</div>
      {novels.map((novel) => {
        const cls = ["spine", novel.isCurrent ? "spine--current" : ""]
          .filter(Boolean)
          .join(" ");
        const href = `/novel/${novel.slug}/1`;
        return (
          <Link
            key={novel.slug}
            href={href}
            className={cls}
            aria-current={novel.isCurrent ? "true" : undefined}
          >
            {novel.name}
          </Link>
        );
      })}
      <button className="bookshelf__add" aria-label="Add a volume" type="button">
        +
      </button>
    </aside>
  );
}

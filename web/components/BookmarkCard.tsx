import Link from "next/link";
import { fetchBookmark, type Bookmark } from "@/lib/api";

async function loadBookmark(): Promise<Bookmark | null> {
  try {
    return await fetchBookmark();
  } catch {
    return null;
  }
}

export async function BookmarkCard() {
  const bookmark = await loadBookmark();
  if (!bookmark) return null;
  return (
    <article className="bookmark" aria-label="Continue reading">
      <span className="bookmark__ribbon" aria-hidden="true" />
      <div className="bookmark__novel">
        <em>{bookmark.novelName}</em>
      </div>
      <h2 className="bookmark__title">{bookmark.title}</h2>
      <p className="bookmark__preview">{bookmark.preview}</p>
      <Link
        href={`/novel/${bookmark.novelSlug}/${bookmark.chapter}`}
        className="link"
      >
        Continue reading
      </Link>
    </article>
  );
}

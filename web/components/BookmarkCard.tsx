import Link from "next/link";
import { bookmark } from "@/lib/mock";

export function BookmarkCard() {
  return (
    <article className="bookmark" aria-label="Continue reading">
      <span className="bookmark__ribbon" aria-hidden="true" />
      <div className="bookmark__novel">
        <em>{bookmark.novel}</em>
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

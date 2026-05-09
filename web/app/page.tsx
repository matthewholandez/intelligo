import { Greeting } from "@/components/Greeting";
import { BookmarkCard } from "@/components/BookmarkCard";
import { ChapterCard } from "@/components/ChapterCard";
import { Press } from "@/components/Press";
import { fetchRecentChapters, type RecentChapter } from "@/lib/api";

async function loadRecent(): Promise<RecentChapter[]> {
  try {
    return await fetchRecentChapters(3);
  } catch {
    return [];
  }
}

export default async function ReadingRoom() {
  const recent = await loadRecent();
  return (
    <section className="room" aria-label="The Reading Room">
      <Greeting />
      <BookmarkCard />

      <h3 className="row-heading">Recently translated</h3>
      <div className="cards">
        {recent.length === 0 ? (
          <p className="card__preview">No chapters yet.</p>
        ) : (
          recent.map((item) => (
            <ChapterCard
              key={`${item.novelSlug}-${item.chapter}`}
              item={item}
            />
          ))
        )}
      </div>

      <h3 className="row-heading">The press</h3>
      <Press />
    </section>
  );
}

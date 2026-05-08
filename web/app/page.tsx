import { Greeting } from "@/components/Greeting";
import { BookmarkCard } from "@/components/BookmarkCard";
import { ChapterCard } from "@/components/ChapterCard";
import { Press } from "@/components/Press";
import { recent } from "@/lib/mock";

export default function ReadingRoom() {
  return (
    <section className="room" aria-label="The Reading Room">
      <Greeting />
      <BookmarkCard />

      <h3 className="row-heading">Recently translated</h3>
      <div className="cards">
        {recent.map((item) => (
          <ChapterCard key={`${item.novelSlug}-${item.chapter}`} item={item} />
        ))}
      </div>

      <h3 className="row-heading">The press</h3>
      <Press />
    </section>
  );
}

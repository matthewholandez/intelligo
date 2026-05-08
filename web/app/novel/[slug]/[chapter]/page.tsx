import Link from "next/link";
import { Deckle } from "@/components/Deckle";
import { Fleuron } from "@/components/Fleuron";
import { Gloss } from "@/components/Gloss";
import { Pagination } from "@/components/Pagination";
import { glossByTerm, sampleChapter } from "@/lib/mock";

export default async function ChapterPage(
  props: PageProps<"/novel/[slug]/[chapter]">,
) {
  const { slug, chapter } = await props.params;
  const ch = sampleChapter; // mock content for first draft
  const chapterNumber = Number(chapter) || ch.number;

  return (
    <section className="chapter-shell" aria-label={`Chapter ${chapterNumber}`}>
      <nav className="chapter-nav">
        <Link href={`/novel/${slug}/${chapterNumber - 1}`}>
          ‹ Chapter {chapterNumber - 1}
        </Link>
        <Link href={`/novel/${slug}/${chapterNumber + 1}`}>
          Chapter {chapterNumber + 1} ›
        </Link>
      </nav>

      <div className="reading-ribbon" aria-hidden="true" />

      <article className="chapter">
        <Deckle />

        <p className="chapter__eyebrow">Chapter {ch.numberWord}</p>
        <h1 className="chapter__title">
          <em>{ch.title}</em>
        </h1>

        <div className="chapter__body">
          <p>
            The morning came in slowly, the way mornings do when nothing is
            waiting for them.{" "}
            <Gloss term="Dokja" entry={glossByTerm.Dokja} /> sat with his back
            to the window and let the page stay open in his lap, unread. The
            light moved across the print and made each line briefly important,
            then unimportant again.
          </p>
          <p>
            He had been told, the night before, that the{" "}
            <Gloss term="Constellations" entry={glossByTerm.Constellations} />{" "}
            had taken an interest in him, which was the kind of news a person
            received without quite knowing what to do with their hands. He had
            put his hands around a cup of tea, then around the cup&apos;s
            saucer, then around nothing.
          </p>
          <p>
            &ldquo;You&apos;re not afraid,&rdquo; she had said, not as a
            question. He had not answered, because the truthful answer was
            complicated and the comforting answer was a lie, and he had grown
            old enough, at last, to refuse both.
          </p>

          <Fleuron variant="scene" />

          <p>
            By noon the rain had thinned the streets of everyone but the
            unlucky and the determined. Dokja was both.{" "}
            <Gloss term="Yoo Sangah" entry={glossByTerm["Yoo Sangah"]} />{" "}
            walked half a step behind him with an umbrella she had not opened,
            holding it the way one holds a closed book — patiently, as if its
            time would come.
          </p>
          <p>
            They reached the door without speaking. It was, against all
            reasonable expectation, exactly as it had been described in the
            book: green, with a small brass plate set just below the handle,
            and a quiet to it that had nothing to do with the absence of sound.
          </p>
          <p>&ldquo;It looks ordinary,&rdquo; she said.</p>
          <p>
            &ldquo;Yes,&rdquo; Dokja said. &ldquo;That&apos;s the trouble.&rdquo;
          </p>

          <Fleuron variant="end" />
        </div>
      </article>

      <Pagination slug={slug} prev={ch.prev} next={ch.next} />
    </section>
  );
}

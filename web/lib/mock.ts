export type NovelSummary = {
  slug: string;
  title: string;
  spineWidth?: "thin" | "wide";
  current?: boolean;
};

export const shelf: NovelSummary[] = [
  { slug: "omniscient-reader", title: "Omniscient Reader", current: true },
  { slug: "tbate", title: "The Beginning After the End", spineWidth: "thin" },
  { slug: "solo-leveling", title: "Solo Leveling", spineWidth: "wide" },
  { slug: "trash-of-the-counts-family", title: "Trash of the Count's Family" },
  { slug: "lord-of-the-mysteries", title: "Lord of the Mysteries", spineWidth: "thin" },
  { slug: "returners-magic", title: "A Returner's Magic Should Be Special" },
];

export const greeting = {
  headline: "Welcome back. You left off mid‑sentence.",
  sub: "Three chapters arrived overnight.",
};

export const bookmark = {
  novel: "Omniscient Reader",
  novelSlug: "omniscient-reader",
  chapter: 23,
  title: "Chapter 23 · The Quiet Door",
  preview:
    "The morning came in slowly, the way mornings do when nothing is waiting for them. Dokja sat with his back to the window and let the page stay open in his lap, unread.",
};

export type RecentChapter = {
  novel: string;
  title: string;
  preview: string;
  chapter: number;
  novelSlug: string;
};

export const recent: RecentChapter[] = [
  {
    novel: "Omniscient Reader",
    novelSlug: "omniscient-reader",
    title: "The Quiet Door",
    preview:
      "The morning came in slowly, the way mornings do when nothing is waiting for them.",
    chapter: 23,
  },
  {
    novel: "Lord of the Mysteries",
    novelSlug: "lord-of-the-mysteries",
    title: "A Letter from the Sea",
    preview:
      "Klein read the envelope twice. The wax was sealed in a green he had only seen once before.",
    chapter: 412,
  },
  {
    novel: "Trash of the Count's Family",
    novelSlug: "trash-of-the-counts-family",
    title: "An Honest Reply",
    preview:
      "Cale frowned. There was no graceful way to lie to a child, and he had spent thirty years practicing only the ungraceful ways.",
    chapter: 188,
  },
];

export type PressItem = {
  novel: string;
  chapter: number;
  status: string;
  attempt: number;
  attemptOf: number;
};

export const press: PressItem[] = [
  { novel: "Omniscient Reader", chapter: 24, status: "consulting the glossary…", attempt: 1, attemptOf: 7 },
  { novel: "Solo Leveling", chapter: 91, status: "setting type…", attempt: 1, attemptOf: 7 },
  { novel: "The Beginning After the End", chapter: 312, status: "reading the previous chapter…", attempt: 2, attemptOf: 7 },
];

export type GlossEntry = {
  source: string;
  preferred: string;
  firstChapter: number;
  tag: "character" | "place" | "technique" | "honorific";
};

export const glossByTerm: Record<string, GlossEntry> = {
  Dokja: { source: "독자 (dokja)", preferred: "Dokja", firstChapter: 1, tag: "character" },
  Constellations: { source: "성좌 (seongjwa)", preferred: "Constellations", firstChapter: 4, tag: "technique" },
  "Yoo Sangah": { source: "유상아 (Yoo Sang-ah)", preferred: "Yoo Sangah", firstChapter: 2, tag: "character" },
};

export type TermRow = {
  source: string;
  preferred: string;
  tag: GlossEntry["tag"];
  chapter: number;
};

export const catalogTerms: TermRow[] = [
  { source: "독자 / dokja", preferred: "Dokja", tag: "character", chapter: 1 },
  { source: "성좌 / seongjwa", preferred: "Constellation", tag: "technique", chapter: 4 },
  { source: "시나리오 / sinario", preferred: "Scenario", tag: "technique", chapter: 2 },
  { source: "유상아 / Yoo Sang-ah", preferred: "Yoo Sangah", tag: "character", chapter: 2 },
  { source: "한수영 / Han Sooyoung", preferred: "Han Sooyoung", tag: "character", chapter: 19 },
  { source: "충무로 / Chungmuro", preferred: "Chungmuro", tag: "place", chapter: 7 },
  { source: "도깨비 / dokkaebi", preferred: "Dokkaebi", tag: "character", chapter: 3 },
  { source: "왕 / wang", preferred: "King", tag: "honorific", chapter: 9 },
  { source: "멸살법 / myeolsalbeop", preferred: "Annihilation Method", tag: "technique", chapter: 11 },
];

export const sampleChapter = {
  slug: "omniscient-reader",
  number: 23,
  numberWord: "Twenty-Three",
  title: "The Quiet Door",
  prev: { number: 22, title: "The Long Hour" },
  next: { number: 24, title: "A Stranger's Errand" },
};

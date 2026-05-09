export type Novel = {
  slug: string;
  name: string;
  isCurrent: boolean;
};

export type ChapterRef = {
  number: number;
  name: string | null;
};

export type GlossaryEntry = {
  term: string;
  translation: string;
  tag: string | null;
};

export type Chapter = {
  number: number;
  name: string | null;
  body: string;
  prev: ChapterRef | null;
  next: ChapterRef | null;
  glossary: GlossaryEntry[];
};

export type Bookmark = {
  novelSlug: string;
  novelName: string;
  chapter: number;
  title: string;
  preview: string;
  chaptersLast24h: number;
};

export type RecentChapter = {
  novel: string;
  novelSlug: string;
  title: string | null;
  preview: string;
  chapter: number;
};

export type PressItem = {
  novel: string;
  chapter: number;
  status: string;
  attempt: number;
  attemptOf: number;
};

export type TermRow = {
  source: string;
  preferred: string;
  tag: string | null;
  chapter: number;
};

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ??
  (typeof window === "undefined" ? "http://127.0.0.1:8000" : "");

async function get<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    cache: "no-store",
    ...init,
  });
  if (!res.ok) {
    throw new Error(`GET ${path} failed: ${res.status}`);
  }
  return (await res.json()) as T;
}

async function getOrNull<T>(path: string): Promise<T | null> {
  const res = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
  if (res.status === 204 || res.status === 404) return null;
  if (!res.ok) throw new Error(`GET ${path} failed: ${res.status}`);
  return (await res.json()) as T;
}

export async function fetchNovels(): Promise<Novel[]> {
  const data = await get<{ items: Novel[] }>("/api/novels");
  return data.items;
}

export async function fetchNovel(slug: string): Promise<Novel | null> {
  return getOrNull<Novel>(`/api/novels/${slug}`);
}

export async function fetchChapter(
  slug: string,
  number: number,
): Promise<Chapter | null> {
  return getOrNull<Chapter>(`/api/novels/${slug}/chapters/${number}`);
}

export async function fetchRecentChapters(
  limit = 3,
): Promise<RecentChapter[]> {
  const data = await get<{ items: RecentChapter[] }>(
    `/api/chapters/recent?limit=${limit}`,
  );
  return data.items;
}

export async function fetchBookmark(): Promise<Bookmark | null> {
  return getOrNull<Bookmark>("/api/bookmark");
}

export async function fetchPress(): Promise<PressItem[]> {
  const data = await get<{ items: PressItem[] }>("/api/press");
  return data.items;
}

export async function fetchGlossary(
  slug: string,
  opts: { q?: string; tag?: string } = {},
): Promise<TermRow[]> {
  const params = new URLSearchParams();
  if (opts.q) params.set("q", opts.q);
  if (opts.tag) params.set("tag", opts.tag);
  const qs = params.toString();
  const data = await get<{ items: TermRow[] }>(
    `/api/novels/${slug}/glossary${qs ? `?${qs}` : ""}`,
  );
  return data.items;
}

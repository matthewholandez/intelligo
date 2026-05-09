import { fetchBookmark } from "@/lib/api";

export async function Greeting() {
  let count = 0;
  try {
    const bookmark = await fetchBookmark();
    count = bookmark?.chaptersLast24h ?? 0;
  } catch {
    count = 0;
  }
  const headline = count
    ? "Welcome back. You left off mid‑sentence."
    : "Welcome to the reading room.";
  const sub =
    count === 0
      ? "Nothing new yet — set up your first volume."
      : count === 1
        ? "One chapter arrived overnight."
        : `${count} chapters arrived overnight.`;
  return (
    <>
      <h1 className="greeting">{headline}</h1>
      <p className="greeting__sub">{sub}</p>
    </>
  );
}

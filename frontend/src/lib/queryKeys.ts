export const queryKeys = {
  novels: ["novels"] as const,
  novel: (id: number) => ["novel", id] as const,
  chapters: (novelId: number) => ["chapters", novelId] as const,
  chapter: (novelId: number, chapId: number) =>
    ["chapter", novelId, chapId] as const,
  glossary: (novelId: number) => ["glossary", novelId] as const,
};

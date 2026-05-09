import { CatalogSearch } from "@/components/CatalogSearch";
import { TermCard } from "@/components/TermCard";
import { fetchGlossary, type TermRow } from "@/lib/api";

export default async function GlossaryPage(
  props: PageProps<"/novel/[slug]/glossary">,
) {
  const { slug } = await props.params;
  let terms: TermRow[];
  try {
    terms = await fetchGlossary(slug);
  } catch {
    terms = [];
  }
  return (
    <section className="catalog" aria-label="Glossary">
      <CatalogSearch />
      <div className="catalog__grid">
        {terms.length === 0 ? (
          <p>No entries yet.</p>
        ) : (
          terms.map((term) => <TermCard key={term.source} term={term} />)
        )}
      </div>
    </section>
  );
}

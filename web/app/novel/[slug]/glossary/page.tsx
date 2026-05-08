import { CatalogSearch } from "@/components/CatalogSearch";
import { TermCard } from "@/components/TermCard";
import { catalogTerms } from "@/lib/mock";

export default async function GlossaryPage(
  _props: PageProps<"/novel/[slug]/glossary">,
) {
  return (
    <section className="catalog" aria-label="Glossary">
      <CatalogSearch />
      <div className="catalog__grid">
        {catalogTerms.map((term) => (
          <TermCard key={term.source} term={term} />
        ))}
      </div>
    </section>
  );
}

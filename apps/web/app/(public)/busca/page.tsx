import { mockMunicipios, mockEmpresas } from "@/lib/mock";
import Link from "next/link";
import { SearchBar } from "@/components/search/search-bar";
import { formatCNPJ } from "@olho/shared";

interface Props {
  searchParams: Promise<{ q?: string }>;
}

export default async function BuscaPage({ searchParams }: Props) {
  const { q = "" } = await searchParams;
  const term = q.toLowerCase().trim();

  const cidades = term
    ? mockMunicipios.filter(
        (m) => m.nome.toLowerCase().includes(term) || m.slug.includes(term)
      )
    : [];

  const cleanQ = term.replace(/\D/g, "");
  const empresas =
    cleanQ.length >= 8 || term.length >= 3
      ? mockEmpresas.filter(
          (e) => e.cnpj.includes(cleanQ) || e.razaoSocial.toLowerCase().includes(term)
        )
      : [];

  return (
    <div className="mx-auto max-w-3xl px-4 py-12">
      <h1 className="text-3xl font-bold mb-6">Busca</h1>
      <SearchBar />
      {term && (
        <div className="mt-8">
          {cidades.length === 0 && empresas.length === 0 && (
            <p className="text-fg-muted">Nenhum resultado para &ldquo;{q}&rdquo;.</p>
          )}
          {cidades.length > 0 && (
            <section className="mb-6">
              <h2 className="text-sm uppercase tracking-wider text-fg-subtle mb-2">Cidades</h2>
              <ul className="space-y-2">
                {cidades.map((c) => (
                  <li key={c.idIbge}>
                    <Link href={`/cidade/${c.uf}/${c.slug}`} className="text-fg hover:underline">
                      {c.nome} <span className="text-fg-subtle">— {c.uf}</span>
                    </Link>
                  </li>
                ))}
              </ul>
            </section>
          )}
          {empresas.length > 0 && (
            <section>
              <h2 className="text-sm uppercase tracking-wider text-fg-subtle mb-2">Empresas</h2>
              <ul className="space-y-2">
                {empresas.map((e) => (
                  <li key={e.cnpj}>
                    <Link href={`/empresa/${e.cnpj}`} className="text-fg hover:underline">
                      {e.razaoSocial}
                    </Link>{" "}
                    <span className="text-xs text-fg-subtle font-mono">{formatCNPJ(e.cnpj)}</span>
                  </li>
                ))}
              </ul>
            </section>
          )}
        </div>
      )}
    </div>
  );
}

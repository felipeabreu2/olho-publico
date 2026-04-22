import Link from "next/link";
import { SearchBar } from "@/components/search/search-bar";
import { AlertCard } from "@/components/alerts/alert-card";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { mockMunicipios, mockAlertasSP } from "@/lib/mock";

export default function HomePage() {
  return (
    <div>
      {/* Hero */}
      <section className="border-b border-border-subtle">
        <div className="mx-auto max-w-4xl px-4 py-20 text-center">
          <h1 className="text-4xl md:text-6xl font-bold tracking-tight text-fg leading-tight">
            Para onde vai o<br />
            <span className="text-fg/70">dinheiro público brasileiro?</span>
          </h1>
          <p className="mt-6 text-lg text-fg-muted max-w-2xl mx-auto">
            Olho Público mostra contratos, fornecedores e sinais de alerta da sua cidade
            usando apenas dados oficiais.
          </p>
          <div className="mt-10">
            <SearchBar size="lg" />
          </div>
        </div>
      </section>

      {/* Cidades em destaque */}
      <section className="mx-auto max-w-6xl px-4 py-16">
        <h2 className="text-2xl font-semibold mb-6">Cidades em destaque</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {mockMunicipios.map((m) => (
            <Link key={m.idIbge} href={`/cidade/${m.uf}/${m.slug}`}>
              <Card className="h-full hover:border-fg/30 transition-colors">
                <CardHeader>
                  <CardTitle>
                    {m.nome}{" "}
                    <span className="text-fg-subtle text-sm font-normal">— {m.uf}</span>
                  </CardTitle>
                  <CardDescription>
                    {m.populacao?.toLocaleString("pt-BR")} habitantes
                  </CardDescription>
                </CardHeader>
                <p className="text-sm text-fg-muted">
                  Prefeito: <span className="text-fg">{m.prefeitoNome}</span> ({m.prefeitoPartido})
                </p>
              </Card>
            </Link>
          ))}
        </div>
      </section>

      {/* Feed nacional de alertas (mock) */}
      <section className="mx-auto max-w-6xl px-4 py-16 border-t border-border-subtle">
        <div className="flex items-end justify-between mb-6">
          <h2 className="text-2xl font-semibold">Sinais recentes</h2>
          <p className="text-sm text-fg-subtle">Detectados automaticamente em dados oficiais</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {mockAlertasSP.map((a) => (
            <AlertCard key={a.id} alerta={a} />
          ))}
        </div>
      </section>
    </div>
  );
}

import Link from "next/link";
import { ArrowRight, Database, Eye, Shield } from "lucide-react";
import { SearchBar } from "@/components/search/search-bar";
import { AlertCard } from "@/components/alerts/alert-card";
import { Card } from "@/components/ui/card";
import { mockMunicipios, mockAlertasSP } from "@/lib/mock";
import { formatNumber } from "@olho/shared";

export default function HomePage() {
  return (
    <div>
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-border-subtle">
        {/* Glow background */}
        <div
          aria-hidden
          className="absolute inset-0 -z-10 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-emerald-500/10 via-transparent to-transparent"
        />
        <div className="mx-auto max-w-5xl px-4 py-24 md:py-32 text-center">
          <div className="inline-flex items-center gap-2 rounded-full border border-border-subtle bg-bg-subtle px-3 py-1 text-xs text-fg-muted mb-6">
            <span className="size-1.5 rounded-full bg-accent-fact animate-pulse" />
            5.570 cidades · dados oficiais CGU, IBGE e Receita
          </div>

          <h1 className="text-5xl md:text-7xl font-bold tracking-tighter text-fg leading-[1.05]">
            Para onde vai o<br />
            <span className="bg-gradient-to-br from-fg to-fg-muted bg-clip-text text-transparent">
              dinheiro público brasileiro?
            </span>
          </h1>

          <p className="mt-6 text-lg md:text-xl text-fg-muted max-w-2xl mx-auto leading-relaxed">
            Digite o nome da sua cidade e veja contratos, fornecedores, repasses
            federais e sinais de alerta — tudo a partir de fontes oficiais.
          </p>

          <div className="mt-10">
            <SearchBar size="lg" />
            <p className="mt-3 text-xs text-fg-subtle">
              Sem cadastro · Sem rastreamento · Código aberto
            </p>
          </div>

          {/* Princípios */}
          <div className="mt-16 grid grid-cols-1 sm:grid-cols-3 gap-4 text-left max-w-3xl mx-auto">
            {[
              {
                icon: Database,
                titulo: "Apenas dados oficiais",
                descricao:
                  "Sem opinião. Tudo vem de Portal da Transparência, IBGE, Receita Federal e CGU.",
              },
              {
                icon: Eye,
                titulo: "Sinais, não acusações",
                descricao:
                  "Cada alerta carrega disclaimer e link para a evidência. Você decide.",
              },
              {
                icon: Shield,
                titulo: "Direito de resposta",
                descricao:
                  "Encontrou um dado errado? Conteste — a correção fica vinculada ao registro.",
              },
            ].map(({ icon: Icon, titulo, descricao }) => (
              <div key={titulo} className="rounded-lg border border-border-subtle bg-bg-subtle/40 p-4">
                <Icon className="size-5 text-fg-muted mb-3" />
                <h3 className="font-medium text-fg mb-1">{titulo}</h3>
                <p className="text-sm text-fg-muted leading-relaxed">{descricao}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Cidades em destaque */}
      <section className="mx-auto max-w-6xl px-4 py-20">
        <div className="flex items-end justify-between mb-8">
          <div>
            <h2 className="text-2xl md:text-3xl font-semibold tracking-tight">
              Cidades em destaque
            </h2>
            <p className="mt-1 text-fg-muted">
              Exemplos de cidades já com dados consolidados
            </p>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {mockMunicipios.map((m) => (
            <Link
              key={m.idIbge}
              href={`/cidade/${m.uf}/${m.slug}`}
              className="group block focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-fg/40 rounded-lg"
            >
              <Card className="h-full transition-all duration-200 group-hover:border-fg/40 group-hover:bg-bg-elevated/60">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="text-xl font-semibold text-fg tracking-tight">
                      {m.nome}
                    </h3>
                    <p className="text-sm text-fg-subtle">{m.uf}</p>
                  </div>
                  <ArrowRight className="size-4 text-fg-subtle transition-transform group-hover:translate-x-1 group-hover:text-fg" />
                </div>
                <dl className="space-y-1.5 text-sm">
                  <div className="flex justify-between">
                    <dt className="text-fg-muted">População</dt>
                    <dd className="font-mono text-fg">
                      {formatNumber(m.populacao ?? 0)}
                    </dd>
                  </div>
                  {m.prefeitoNome && (
                    <div className="flex justify-between">
                      <dt className="text-fg-muted">Prefeito(a)</dt>
                      <dd className="text-fg truncate ml-2">
                        {m.prefeitoNome}
                      </dd>
                    </div>
                  )}
                </dl>
              </Card>
            </Link>
          ))}
        </div>
      </section>

      {/* Feed nacional de alertas */}
      <section className="mx-auto max-w-6xl px-4 py-20 border-t border-border-subtle">
        <div className="flex items-end justify-between mb-8">
          <div>
            <h2 className="text-2xl md:text-3xl font-semibold tracking-tight">
              Sinais recentes
            </h2>
            <p className="mt-1 text-fg-muted">
              Detectados automaticamente nos dados oficiais
            </p>
          </div>
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

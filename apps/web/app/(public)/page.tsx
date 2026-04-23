import Link from "next/link";
import { ArrowRight, Database, Eye, Shield, AlertTriangle } from "lucide-react";
import { SearchBar } from "@/components/search/search-bar";
import { AlertCard } from "@/components/alerts/alert-card";
import { Card } from "@/components/ui/card";
import { mockMunicipios, mockAlertasSP } from "@/lib/mock";
import {
  getHomeStats,
  getSancoesRecentes,
  getTopCidades,
  type CidadeDestaque,
  type HomeStats,
  type SancaoRecente,
} from "@/lib/queries/home";
import { formatBRLCompact, formatCNPJ, formatDate, formatNumber } from "@olho/shared";

export const revalidate = 3600; // 1h ISR

async function loadStats(): Promise<HomeStats | null> {
  try {
    return await getHomeStats();
  } catch {
    return null;
  }
}

async function loadTopCidades(): Promise<CidadeDestaque[]> {
  try {
    const real = await getTopCidades(6);
    if (real.length > 0) return real;
  } catch {
    /* fallback */
  }
  return [];
}

async function loadSancoes(): Promise<SancaoRecente[]> {
  try {
    return await getSancoesRecentes(6);
  } catch {
    return [];
  }
}

export default async function HomePage() {
  const [stats, topCidades, sancoes] = await Promise.all([
    loadStats(),
    loadTopCidades(),
    loadSancoes(),
  ]);

  // Fallback: se não tiver dados reais, mostra mock pra não quebrar
  const cidadesParaMostrar =
    topCidades.length > 0
      ? topCidades
      : mockMunicipios.map((m) => ({
          idIbge: m.idIbge,
          nome: m.nome,
          uf: m.uf,
          slug: m.slug,
          populacao: m.populacao,
          totalContratosFederais: "0",
          qtdContratosFederais: 0,
        }));

  return (
    <div>
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-border-subtle">
        <div
          aria-hidden
          className="absolute inset-0 -z-10 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-emerald-500/10 via-transparent to-transparent"
        />
        <div className="mx-auto max-w-5xl px-4 py-24 md:py-32 text-center">
          <div className="inline-flex items-center gap-2 rounded-full border border-border-subtle bg-bg-subtle px-3 py-1 text-xs text-fg-muted mb-6">
            <span className="size-1.5 rounded-full bg-accent-fact animate-pulse" />
            {stats
              ? `${formatNumber(stats.totalMunicipios)} cidades · ${formatNumber(stats.totalContratos)} contratos · dados oficiais`
              : "5.570 cidades · dados oficiais CGU, IBGE e Receita"}
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
        </div>
      </section>

      {/* KPIs nacionais */}
      {stats && stats.totalContratos > 0 && (
        <section className="border-b border-border-subtle bg-bg-subtle/30">
          <div className="mx-auto max-w-6xl px-4 py-12">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <KpiTile
                label="Municípios"
                value={formatNumber(stats.totalMunicipios)}
                hint="cobertos pela base"
              />
              <KpiTile
                label="Contratos federais"
                value={formatNumber(stats.totalContratos)}
                hint={`R$ ${formatBRLCompact(stats.valorTotalContratos)}`}
              />
              <KpiTile
                label="Empresas catalogadas"
                value={formatNumber(stats.totalEmpresas)}
                hint="recebem ou fornecem"
              />
              <KpiTile
                label="Sanções vigentes"
                value={formatNumber(stats.totalSancoes)}
                hint="CEIS + CNEP + CEPIM"
              />
            </div>
          </div>
        </section>
      )}

      {/* Princípios */}
      <section className="mx-auto max-w-5xl px-4 py-16">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
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
            <div
              key={titulo}
              className="rounded-lg border border-border-subtle bg-bg-subtle/40 p-5"
            >
              <Icon className="size-5 text-fg-muted mb-3" />
              <h3 className="font-medium text-fg mb-1">{titulo}</h3>
              <p className="text-sm text-fg-muted leading-relaxed">{descricao}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Top cidades por valor recebido */}
      <section className="mx-auto max-w-6xl px-4 py-16 border-t border-border-subtle">
        <div className="flex items-end justify-between mb-8">
          <div>
            <h2 className="text-2xl md:text-3xl font-semibold tracking-tight">
              {topCidades.length > 0
                ? "Cidades que mais receberam"
                : "Cidades em destaque"}
            </h2>
            <p className="mt-1 text-fg-muted">
              {topCidades.length > 0
                ? "Por valor de contratos federais agregados"
                : "Exemplos de cidades para explorar"}
            </p>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {cidadesParaMostrar.map((m, idx) => (
            <Link
              key={m.idIbge}
              href={`/cidade/${m.uf}/${m.slug}`}
              className="group block focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-fg/40 rounded-lg"
            >
              <Card className="h-full transition-all duration-200 group-hover:border-fg/40 group-hover:bg-bg-elevated/60">
                <div className="flex items-start justify-between mb-3">
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2 mb-0.5">
                      <span className="text-xs font-mono text-fg-subtle tabular-nums">
                        {String(idx + 1).padStart(2, "0")}.
                      </span>
                      <h3 className="text-lg font-semibold text-fg tracking-tight truncate">
                        {m.nome}
                      </h3>
                    </div>
                    <p className="text-xs text-fg-subtle ml-7">
                      {m.uf}
                      {m.populacao ? ` · ${formatNumber(m.populacao)} hab` : ""}
                    </p>
                  </div>
                  <ArrowRight className="size-4 text-fg-subtle transition-transform group-hover:translate-x-1 group-hover:text-fg shrink-0 mt-1" />
                </div>
                {parseFloat(m.totalContratosFederais) > 0 && (
                  <dl className="space-y-1 text-sm pt-3 border-t border-border-subtle">
                    <div className="flex justify-between">
                      <dt className="text-fg-muted">Federal recebido</dt>
                      <dd className="font-mono font-semibold text-fg">
                        {formatBRLCompact(m.totalContratosFederais)}
                      </dd>
                    </div>
                    <div className="flex justify-between">
                      <dt className="text-fg-muted">Contratos</dt>
                      <dd className="font-mono text-fg-subtle">
                        {formatNumber(m.qtdContratosFederais)}
                      </dd>
                    </div>
                  </dl>
                )}
              </Card>
            </Link>
          ))}
        </div>
      </section>

      {/* Sanções recentes (real) ou Alertas mock */}
      {sancoes.length > 0 ? (
        <section className="mx-auto max-w-6xl px-4 py-16 border-t border-border-subtle">
          <div className="flex items-end justify-between mb-8">
            <div>
              <h2 className="text-2xl md:text-3xl font-semibold tracking-tight">
                Sanções recentes
              </h2>
              <p className="mt-1 text-fg-muted">
                Empresas inidôneas, punidas ou impedidas pelo governo federal
              </p>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {sancoes.map((s) => (
              <Card key={`${s.cnpj}-${s.dataInicio}`} className="border-l-4 border-l-accent-strong">
                <div className="flex items-center gap-2 mb-2">
                  <AlertTriangle className="size-3 text-accent-strong shrink-0" />
                  <span className="text-xs uppercase tracking-wider text-accent-strong font-medium">
                    {s.tipoSancao}
                  </span>
                </div>
                <Link
                  href={`/empresa/${s.cnpj}`}
                  className="block font-semibold text-fg leading-snug hover:underline mb-1"
                >
                  {s.razaoSocial || formatCNPJ(s.cnpj)}
                </Link>
                <p className="text-xs text-fg-subtle font-mono mb-2">
                  {formatCNPJ(s.cnpj)}
                </p>
                <p className="text-sm text-fg-muted">
                  Sancionada por: <span className="text-fg">{s.orgaoSancionador}</span>
                </p>
                <p className="text-xs text-fg-subtle mt-2">
                  Início: {formatDate(s.dataInicio)}
                </p>
              </Card>
            ))}
          </div>
        </section>
      ) : (
        <section className="mx-auto max-w-6xl px-4 py-16 border-t border-border-subtle">
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
      )}
    </div>
  );
}

function KpiTile({
  label,
  value,
  hint,
}: {
  label: string;
  value: string;
  hint?: string;
}) {
  return (
    <div>
      <p className="text-xs uppercase tracking-wider text-fg-subtle font-medium mb-1.5">
        {label}
      </p>
      <p className="font-mono text-3xl md:text-4xl font-semibold text-fg tabular-nums tracking-tight">
        {value}
      </p>
      {hint && <p className="text-xs text-fg-muted mt-1">{hint}</p>}
    </div>
  );
}

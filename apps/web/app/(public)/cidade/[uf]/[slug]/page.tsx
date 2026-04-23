import { notFound } from "next/navigation";
import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { AlertCard } from "@/components/alerts/alert-card";
import { TopFornecedores } from "@/components/city/top-fornecedores";
import { GastosPorArea } from "@/components/city/gastos-por-area";
import { ComparacaoSimilares } from "@/components/city/comparacao-similares";
import { mockMunicipios, mockAgregacoes, mockAlertasSP } from "@/lib/mock";
import { getMunicipioBySlug } from "@/lib/queries/municipios";
import { getAgregacaoAno } from "@/lib/queries/agregacoes";
import { formatBRLCompact, formatNumber } from "@olho/shared";
import { BarChart3 } from "lucide-react";

export const revalidate = 21600; // 6h ISR

interface Props {
  params: Promise<{ uf: string; slug: string }>;
}

async function loadMunicipio(uf: string, slug: string) {
  try {
    const real = await getMunicipioBySlug(uf, slug);
    if (real) return real;
  } catch {
    // Banco indisponível — cai no mock
  }
  return mockMunicipios.find((m) => m.uf === uf.toUpperCase() && m.slug === slug) ?? null;
}

async function loadAgregacao(municipioId: string) {
  const ano = new Date().getFullYear();
  try {
    const ag = await getAgregacaoAno(municipioId, ano);
    if (ag) return ag;
  } catch {
    // fallback
  }
  return mockAgregacoes[municipioId] ?? null;
}

export async function generateMetadata({ params }: Props) {
  const { uf, slug } = await params;
  const m = await loadMunicipio(uf, slug);
  if (!m) return {};
  const ag = await loadAgregacao(m.idIbge);
  const total = ag ? formatBRLCompact(ag.totalContratosFederais) : "";
  return {
    title: `${m.nome} — ${m.uf}`,
    description: total
      ? `${m.nome} (${m.uf}) recebeu ${total} em contratos federais. Veja sinais detectados e maiores fornecedores.`
      : `Dados públicos de ${m.nome}, ${m.uf}.`,
  };
}

export default async function CidadePage({ params }: Props) {
  const { uf, slug } = await params;
  const municipio = await loadMunicipio(uf, slug);
  if (!municipio) notFound();
  const agregacoes = await loadAgregacao(municipio.idIbge);
  const alertas = municipio.idIbge === "3550308" ? mockAlertasSP : [];

  return (
    <div className="mx-auto max-w-5xl px-4 py-12">
      <header className="mb-10">
        <div className="flex items-center gap-2 mb-2">
          <Link href="/" className="text-sm text-fg-subtle hover:text-fg">Início</Link>
          <span className="text-fg-subtle">/</span>
          <span className="text-sm text-fg-subtle">{municipio.uf}</span>
        </div>
        <h1 className="text-4xl font-bold tracking-tight">{municipio.nome}</h1>
        <p className="mt-2 text-fg-muted">
          {municipio.uf} · {formatNumber(municipio.populacao ?? 0)} habitantes
          {municipio.prefeitoNome && (
            <>
              {" "}· Prefeito(a): <span className="text-fg">{municipio.prefeitoNome}</span>
              {municipio.prefeitoPartido && ` (${municipio.prefeitoPartido})`}
            </>
          )}
        </p>
        <div className="mt-4 flex items-center gap-3">
          <Badge variant="muted">Cobertura prefeitura: {municipio.coberturaPrefeitura}</Badge>
          {municipio.erpDetectado && <Badge variant="muted">ERP: {municipio.erpDetectado}</Badge>}
          <Link href={`/cidade/${municipio.uf}/${municipio.slug}/dashboard`}>
            <Button variant="secondary" size="sm">
              <BarChart3 className="size-4 mr-2" /> Ver dashboard completo
            </Button>
          </Link>
        </div>
      </header>

      {agregacoes && (
        <section className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-10">
          <KpiCard label="Contratos federais" value={formatBRLCompact(agregacoes.totalContratosFederais)} />
          <KpiCard label="Contratos prefeitura" value={formatBRLCompact(agregacoes.totalContratosPrefeitura)} />
          <KpiCard label="Total de contratos" value={formatNumber(agregacoes.qtdContratosFederais + agregacoes.qtdContratosPrefeitura)} />
          <KpiCard label="Sinais detectados" value={String(alertas.length)} highlight={alertas.length > 0} />
        </section>
      )}

      {alertas.length > 0 && (
        <section className="mb-10">
          <h2 className="text-xl font-semibold mb-4">Sinais detectados</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {alertas.map((a) => <AlertCard key={a.id} alerta={a} />)}
          </div>
        </section>
      )}

      {agregacoes && agregacoes.topFornecedores.length > 0 && (
        <section className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-10">
          <TopFornecedores items={agregacoes.topFornecedores} />
          {agregacoes.gastosPorArea.length > 0 && <GastosPorArea items={agregacoes.gastosPorArea} />}
        </section>
      )}

      {agregacoes && agregacoes.comparacaoSimilares.length > 0 && (
        <section className="mb-10">
          <ComparacaoSimilares items={agregacoes.comparacaoSimilares} />
        </section>
      )}

      {!agregacoes && (
        <div className="rounded-lg border border-dashed border-border p-8 text-center">
          <p className="text-fg-muted">
            Ainda estamos consolidando os dados desta cidade. Volte em breve.
          </p>
        </div>
      )}
    </div>
  );
}

function KpiCard({
  label,
  value,
  highlight = false,
}: {
  label: string;
  value: string;
  highlight?: boolean;
}) {
  return (
    <div className="rounded-lg border border-border bg-bg-subtle p-4">
      <p className="text-xs uppercase tracking-wider text-fg-subtle">{label}</p>
      <p className={`mt-1 font-mono text-xl font-semibold ${highlight ? "text-accent-strong" : "text-fg"}`}>
        {value}
      </p>
    </div>
  );
}

import { notFound } from "next/navigation";
import Link from "next/link";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { mockMunicipios, mockAgregacoes } from "@/lib/mock";
import { formatBRL, formatNumber } from "@olho/shared";
import { ArrowLeft } from "lucide-react";

interface Props {
  params: Promise<{ uf: string; slug: string }>;
}

export default async function DashboardCidade({ params }: Props) {
  const { uf, slug } = await params;
  const municipio = mockMunicipios.find((m) => m.uf === uf.toUpperCase() && m.slug === slug);
  if (!municipio) notFound();
  const ag = mockAgregacoes[municipio.idIbge];

  return (
    <div className="mx-auto max-w-6xl px-4 py-12">
      <div className="flex items-center justify-between mb-8">
        <div>
          <Link
            href={`/cidade/${municipio.uf}/${municipio.slug}`}
            className="text-sm text-fg-subtle hover:text-fg flex items-center gap-1"
          >
            <ArrowLeft className="size-3" /> Voltar para visão geral
          </Link>
          <h1 className="mt-2 text-3xl font-bold">{municipio.nome} — Dashboard</h1>
        </div>
      </div>

      {!ag && <p className="text-fg-muted">Sem dados consolidados.</p>}

      {ag && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <Card>
            <CardHeader>
              <CardTitle>Total contratos federais</CardTitle>
            </CardHeader>
            <p className="font-mono text-2xl">{formatBRL(ag.totalContratosFederais)}</p>
            <p className="text-sm text-fg-muted mt-1">
              {formatNumber(ag.qtdContratosFederais)} contratos
            </p>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Total contratos prefeitura</CardTitle>
            </CardHeader>
            <p className="font-mono text-2xl">{formatBRL(ag.totalContratosPrefeitura)}</p>
            <p className="text-sm text-fg-muted mt-1">
              {formatNumber(ag.qtdContratosPrefeitura)} contratos
            </p>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>População</CardTitle>
            </CardHeader>
            <p className="font-mono text-2xl">{formatNumber(municipio.populacao ?? 0)}</p>
          </Card>
          <Card className="md:col-span-2 lg:col-span-3">
            <CardHeader>
              <CardTitle>Top 10 fornecedores</CardTitle>
            </CardHeader>
            <table className="w-full text-sm">
              <thead className="text-fg-subtle text-xs uppercase tracking-wider">
                <tr>
                  <th className="text-left pb-2">Empresa</th>
                  <th className="text-left pb-2">CNPJ</th>
                  <th className="text-right pb-2">Contratos</th>
                  <th className="text-right pb-2">Valor total</th>
                </tr>
              </thead>
              <tbody>
                {ag.topFornecedores.map((f) => (
                  <tr key={f.cnpj} className="border-t border-border-subtle">
                    <td className="py-2">
                      <Link href={`/empresa/${f.cnpj}`} className="hover:underline">
                        {f.razaoSocial}
                      </Link>
                    </td>
                    <td className="py-2 font-mono text-fg-muted">{f.cnpj}</td>
                    <td className="py-2 text-right font-mono">{f.totalContratos}</td>
                    <td className="py-2 text-right font-mono">{formatBRL(f.valorTotal)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        </div>
      )}
    </div>
  );
}

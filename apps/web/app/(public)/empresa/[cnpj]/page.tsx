import { notFound } from "next/navigation";
import Link from "next/link";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { mockEmpresas } from "@/lib/mock";
import { formatCNPJ, formatDate } from "@olho/shared";

interface Props {
  params: Promise<{ cnpj: string }>;
}

export default async function EmpresaPage({ params }: Props) {
  const { cnpj } = await params;
  const cleanCnpj = cnpj.replace(/\D/g, "");
  const empresa = mockEmpresas.find((e) => e.cnpj === cleanCnpj);
  if (!empresa) notFound();

  const flagsAtivas = Object.entries(empresa.flags).filter(([, v]) => v);

  return (
    <div className="mx-auto max-w-3xl px-4 py-12">
      <header className="mb-8">
        <p className="text-sm text-fg-subtle font-mono">{formatCNPJ(empresa.cnpj)}</p>
        <h1 className="mt-1 text-3xl font-bold">{empresa.razaoSocial}</h1>
        {empresa.nomeFantasia && <p className="text-fg-muted">{empresa.nomeFantasia}</p>}
        <div className="mt-3 flex flex-wrap gap-2">
          {empresa.situacao && <Badge variant="muted">{empresa.situacao}</Badge>}
          {flagsAtivas.map(([k]) => (
            <Badge
              key={k}
              variant={k === "sancionada" ? "strong" : k === "foguete" ? "attention" : "fact"}
            >
              {k}
            </Badge>
          ))}
        </div>
      </header>

      <Card className="mb-4">
        <CardHeader>
          <CardTitle>Dados cadastrais</CardTitle>
          <CardDescription>Fonte: Receita Federal</CardDescription>
        </CardHeader>
        <dl className="grid grid-cols-2 gap-3 text-sm">
          <div>
            <dt className="text-fg-subtle">Abertura</dt>
            <dd className="text-fg">{empresa.dataAbertura ? formatDate(empresa.dataAbertura) : "—"}</dd>
          </div>
          <div>
            <dt className="text-fg-subtle">CNAE principal</dt>
            <dd className="text-fg font-mono">{empresa.cnaePrincipal ?? "—"}</dd>
          </div>
          <div>
            <dt className="text-fg-subtle">Sede</dt>
            <dd className="text-fg">{empresa.municipioSedeId ?? "—"}</dd>
          </div>
        </dl>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Contratos públicos, sanções, doações</CardTitle>
          <CardDescription>
            Esta seção é populada após a ingestão dos dados (V2). Por ora, exibimos apenas o cadastro.
          </CardDescription>
        </CardHeader>
        <div className="text-sm text-fg-muted">
          <p>
            Volte em breve. Veja a{" "}
            <Link href="/metodologia" className="underline">
              metodologia
            </Link>{" "}
            para entender as fontes.
          </p>
        </div>
      </Card>
    </div>
  );
}

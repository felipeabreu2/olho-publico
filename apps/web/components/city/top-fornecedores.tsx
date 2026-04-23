import Link from "next/link";
import { ArrowUpRight } from "lucide-react";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { formatBRLCompact, formatCNPJ } from "@olho/shared";

interface TopFornecedor {
  cnpj: string;
  razaoSocial: string;
  totalContratos: number;
  valorTotal: string;
}

export function TopFornecedores({ items }: { items: TopFornecedor[] }) {
  // calcula percent relativo ao maior pra largura das barras
  const maxValor = Math.max(...items.map((f) => parseFloat(f.valorTotal)), 1);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Maiores fornecedores</CardTitle>
        <CardDescription>Empresas que mais receberam neste período</CardDescription>
      </CardHeader>
      <ol className="space-y-3">
        {items.map((f, idx) => {
          const valor = parseFloat(f.valorTotal);
          const pct = (valor / maxValor) * 100;
          return (
            <li key={f.cnpj} className="group">
              <Link
                href={`/empresa/${f.cnpj}`}
                className="block rounded-md p-2 -m-2 transition-colors hover:bg-bg-elevated focus-visible:bg-bg-elevated focus-visible:outline-none"
              >
                <div className="flex items-center justify-between gap-3 mb-1.5">
                  <div className="flex items-center gap-2 min-w-0">
                    <span className="text-xs font-mono text-fg-subtle tabular-nums w-5 text-right">
                      {idx + 1}.
                    </span>
                    <span className="font-medium text-fg truncate group-hover:underline underline-offset-2">
                      {f.razaoSocial}
                    </span>
                    <ArrowUpRight className="size-3.5 text-fg-subtle opacity-0 group-hover:opacity-100 transition-opacity shrink-0" />
                  </div>
                  <div className="text-right shrink-0">
                    <p className="font-mono font-semibold text-fg tabular-nums">
                      {formatBRLCompact(valor)}
                    </p>
                  </div>
                </div>
                <div className="ml-7 flex items-center gap-3">
                  <div className="flex-1 h-1.5 rounded-full bg-bg-elevated overflow-hidden">
                    <div
                      className="h-full rounded-full bg-fg/40 transition-all"
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                  <p className="text-xs text-fg-subtle font-mono w-32 text-right shrink-0">
                    {formatCNPJ(f.cnpj)} · {f.totalContratos}{" "}
                    {f.totalContratos === 1 ? "contrato" : "contratos"}
                  </p>
                </div>
              </Link>
            </li>
          );
        })}
      </ol>
    </Card>
  );
}

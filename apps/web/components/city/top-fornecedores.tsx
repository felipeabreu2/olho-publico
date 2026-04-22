import Link from "next/link";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { formatBRLCompact, formatCNPJ } from "@olho/shared";

interface TopFornecedor {
  cnpj: string;
  razaoSocial: string;
  totalContratos: number;
  valorTotal: string;
}

export function TopFornecedores({ items }: { items: TopFornecedor[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Maiores fornecedores</CardTitle>
      </CardHeader>
      <ul className="divide-y divide-border-subtle">
        {items.map((f) => (
          <li key={f.cnpj} className="py-3 first:pt-0 last:pb-0 flex items-center justify-between gap-3">
            <div className="min-w-0">
              <Link
                href={`/empresa/${f.cnpj}`}
                className="font-medium text-fg hover:underline truncate block"
              >
                {f.razaoSocial}
              </Link>
              <p className="text-xs text-fg-subtle font-mono">{formatCNPJ(f.cnpj)}</p>
            </div>
            <div className="text-right shrink-0">
              <p className="font-mono font-semibold text-fg">{formatBRLCompact(f.valorTotal)}</p>
              <p className="text-xs text-fg-subtle">{f.totalContratos} contratos</p>
            </div>
          </li>
        ))}
      </ul>
    </Card>
  );
}

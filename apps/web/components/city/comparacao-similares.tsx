import Link from "next/link";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";

interface ComparacaoSimilar {
  municipioId: string;
  municipioNome: string;
  uf: string;
  metric: string;
  valorComparado: string;
}

export function ComparacaoSimilares({ items }: { items: ComparacaoSimilar[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Comparação com cidades similares</CardTitle>
        <CardDescription>
          Razão entre o gasto desta cidade e o gasto da cidade comparada (1.0 = igual).
        </CardDescription>
      </CardHeader>
      <ul className="divide-y divide-border-subtle">
        {items.map((c) => (
          <li key={c.municipioId} className="py-3 first:pt-0 last:pb-0 flex items-center justify-between">
            <Link
              href={`/cidade/${c.uf}/${c.municipioId}`}
              className="text-fg hover:underline"
            >
              {c.municipioNome} <span className="text-fg-subtle">— {c.uf}</span>
            </Link>
            <span className="font-mono text-sm">{c.valorComparado}x</span>
          </li>
        ))}
      </ul>
    </Card>
  );
}

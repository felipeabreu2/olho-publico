import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { formatBRLCompact } from "@olho/shared";

interface GastoArea {
  area: string;
  valor: string;
  percentual: number;
}

export function GastosPorArea({ items }: { items: GastoArea[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Gastos por área</CardTitle>
      </CardHeader>
      <ul className="space-y-3">
        {items.map((g) => (
          <li key={g.area}>
            <div className="flex items-center justify-between text-sm mb-1">
              <span className="text-fg">{g.area}</span>
              <span className="font-mono text-fg-muted">{formatBRLCompact(g.valor)}</span>
            </div>
            <div className="h-2 rounded-full bg-bg-elevated overflow-hidden">
              <div
                className="h-full bg-fg/80"
                style={{ width: `${g.percentual}%` }}
                aria-label={`${g.percentual}%`}
              />
            </div>
          </li>
        ))}
      </ul>
    </Card>
  );
}

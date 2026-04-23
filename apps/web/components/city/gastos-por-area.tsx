import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { DonutChart } from "@/components/charts/donut-chart";

interface GastoArea {
  area: string;
  valor: string;
  percentual: number;
}

export function GastosPorArea({ items }: { items: GastoArea[] }) {
  const data = items.map((g) => ({
    label: g.area,
    value: parseFloat(g.valor),
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>Gastos por área</CardTitle>
        <CardDescription>Distribuição percentual do orçamento</CardDescription>
      </CardHeader>
      <DonutChart data={data} height={240} />
    </Card>
  );
}

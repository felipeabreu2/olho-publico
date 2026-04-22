import Link from "next/link";
import type { AlertaDisplay } from "@olho/shared";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { formatDate } from "@olho/shared";

const severidadeLabel = {
  info: "Informativo",
  atencao: "Atenção",
  forte: "Sinal forte",
} as const;

const severidadeVariant = {
  info: "fact",
  atencao: "attention",
  forte: "strong",
} as const;

export function AlertCard({ alerta }: { alerta: AlertaDisplay }) {
  return (
    <Card
      className="border-l-4 data-[severidade=info]:border-l-accent-fact data-[severidade=atencao]:border-l-accent-attention data-[severidade=forte]:border-l-accent-strong"
      data-severidade={alerta.severidade}
    >
      <div className="flex items-start justify-between gap-3 mb-2">
        <Badge variant={severidadeVariant[alerta.severidade]}>
          {severidadeLabel[alerta.severidade]}
        </Badge>
        <time className="text-xs text-fg-subtle">
          {formatDate(alerta.dataDeteccao)}
        </time>
      </div>
      <h4 className="font-semibold text-fg leading-snug mb-1">
        {alerta.tituloLegivel}
      </h4>
      <p className="text-sm text-fg-muted leading-relaxed">
        {alerta.resumoLegivel}
      </p>
      <div className="mt-3 pt-3 border-t border-border-subtle text-xs text-fg-subtle">
        <p className="italic mb-2">{alerta.disclaimer}</p>
        <Link href={alerta.metodologiaUrl} className="hover:text-fg underline-offset-2 hover:underline">
          Ver metodologia desta regra →
        </Link>
      </div>
    </Card>
  );
}

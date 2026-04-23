import Link from "next/link";
import { AlertTriangle, AlertCircle, Info } from "lucide-react";
import type { AlertaDisplay, SeveridadeAlerta } from "@olho/shared";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { formatDate } from "@olho/shared";

const severidadeMeta: Record<
  SeveridadeAlerta,
  { label: string; variant: "fact" | "attention" | "strong"; icon: typeof Info }
> = {
  info: { label: "Informativo", variant: "fact", icon: Info },
  atencao: { label: "Atenção", variant: "attention", icon: AlertCircle },
  forte: { label: "Sinal forte", variant: "strong", icon: AlertTriangle },
};

export function AlertCard({ alerta }: { alerta: AlertaDisplay }) {
  const meta = severidadeMeta[alerta.severidade];
  const Icon = meta.icon;

  return (
    <Card
      className="
        border-l-4 transition-colors hover:bg-bg-subtle/80
        data-[severidade=info]:border-l-accent-fact
        data-[severidade=atencao]:border-l-accent-attention
        data-[severidade=forte]:border-l-accent-strong
      "
      data-severidade={alerta.severidade}
    >
      <div className="flex items-start justify-between gap-3 mb-3">
        <Badge variant={meta.variant} className="gap-1">
          <Icon className="size-3" />
          {meta.label}
        </Badge>
        <time className="text-xs text-fg-subtle font-mono shrink-0">
          {formatDate(alerta.dataDeteccao)}
        </time>
      </div>
      <h4 className="font-semibold text-fg leading-snug text-base mb-1.5 tracking-tight">
        {alerta.tituloLegivel}
      </h4>
      <p className="text-sm text-fg-muted leading-relaxed">{alerta.resumoLegivel}</p>
      <div className="mt-4 pt-3 border-t border-border-subtle space-y-2">
        <p className="text-xs text-fg-subtle italic leading-relaxed">{alerta.disclaimer}</p>
        <Link
          href={alerta.metodologiaUrl}
          className="text-xs text-fg-subtle hover:text-fg underline-offset-2 hover:underline inline-flex items-center gap-1 transition-colors"
        >
          Ver metodologia desta regra
          <span aria-hidden>→</span>
        </Link>
      </div>
    </Card>
  );
}

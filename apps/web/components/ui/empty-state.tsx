import type { LucideIcon } from "lucide-react";
import { cn } from "@/lib/cn";

interface EmptyStateProps {
  icon?: LucideIcon;
  title: string;
  description?: string;
  action?: React.ReactNode;
  className?: string;
}

export function EmptyState({
  icon: Icon,
  title,
  description,
  action,
  className,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        "rounded-lg border border-dashed border-border-subtle bg-bg-subtle/40",
        "p-10 text-center flex flex-col items-center gap-3",
        className
      )}
    >
      {Icon && (
        <div className="size-12 rounded-full bg-bg-elevated flex items-center justify-center">
          <Icon className="size-6 text-fg-subtle" />
        </div>
      )}
      <div className="space-y-1">
        <h3 className="text-base font-semibold text-fg">{title}</h3>
        {description && (
          <p className="text-sm text-fg-muted max-w-sm mx-auto">{description}</p>
        )}
      </div>
      {action && <div className="mt-2">{action}</div>}
    </div>
  );
}

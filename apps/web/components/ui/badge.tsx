import { cn } from "@/lib/cn";
import { cva, type VariantProps } from "class-variance-authority";

const badgeVariants = cva(
  "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium border",
  {
    variants: {
      variant: {
        default: "bg-bg-elevated border-border text-fg",
        fact: "bg-emerald-950/40 border-emerald-800/50 text-emerald-400",
        attention: "bg-amber-950/40 border-amber-800/50 text-amber-400",
        strong: "bg-red-950/40 border-red-800/50 text-red-400",
        muted: "bg-bg-subtle border-border-subtle text-fg-muted",
      },
    },
    defaultVariants: { variant: "default" },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return <span className={cn(badgeVariants({ variant }), className)} {...props} />;
}

import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/utils/cn";

const statusBadgeVariants = cva("inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium", {
  variants: {
    tone: {
      neutral: "bg-muted text-muted-foreground",
      success: "bg-emerald-500/15 text-emerald-600",
      warning: "bg-amber-500/15 text-amber-600",
      danger: "bg-destructive/15 text-destructive",
      info: "bg-primary/15 text-primary dark:bg-purple-400/15 dark:text-purple-300"
    }
  },
  defaultVariants: {
    tone: "neutral"
  }
});

interface StatusBadgeProps extends VariantProps<typeof statusBadgeVariants> {
  label: string;
}

export function StatusBadge({ label, tone }: StatusBadgeProps) {
  return <span className={cn(statusBadgeVariants({ tone }))}>{label}</span>;
}

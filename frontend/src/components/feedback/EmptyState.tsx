import { Inbox } from "lucide-react";
import { Button } from "@/components/ui/button";

interface EmptyStateProps {
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
}

export function EmptyState({ title, description, actionLabel, onAction }: EmptyStateProps) {
  return (
    <div className="grid min-h-[220px] place-items-center rounded-lg border border-dashed bg-card p-6 text-center">
      <div className="max-w-sm space-y-3">
        <div className="mx-auto grid h-10 w-10 place-items-center rounded-full bg-primary/10 text-primary">
          <Inbox className="h-5 w-5" />
        </div>
        <h3 className="text-lg font-semibold">{title}</h3>
        <p className="text-sm text-muted-foreground">{description}</p>
        {actionLabel && onAction ? (
          <Button onClick={onAction} size="sm" variant="outline">
            {actionLabel}
          </Button>
        ) : null}
      </div>
    </div>
  );
}

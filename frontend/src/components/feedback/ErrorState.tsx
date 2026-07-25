import { AlertTriangle, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ErrorStateProps {
  title?: string;
  description?: string;
  onRetry?: () => void;
}

export function ErrorState({
  title = "Something went wrong",
  description = "We could not load this section. Please try again.",
  onRetry
}: ErrorStateProps) {
  return (
    <div className="rounded-lg border bg-card p-5">
      <div className="flex items-start gap-3">
        <div className="mt-0.5 grid h-8 w-8 place-items-center rounded-full bg-destructive/10 text-destructive">
          <AlertTriangle className="h-4 w-4" />
        </div>
        <div className="flex-1 space-y-1">
          <h3 className="text-sm font-semibold">{title}</h3>
          <p className="text-sm text-muted-foreground">{description}</p>
        </div>
        {onRetry ? (
          <Button onClick={onRetry} size="sm" variant="outline">
            <RotateCcw className="mr-2 h-4 w-4" />
            Retry
          </Button>
        ) : null}
      </div>
    </div>
  );
}

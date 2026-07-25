interface LoadingStateProps {
  label?: string;
}

export function LoadingState({ label = "Loading data..." }: LoadingStateProps) {
  return (
    <div className="flex items-center gap-3 rounded-lg border bg-card px-4 py-3 text-sm text-muted-foreground">
      <span className="inline-flex h-4 w-4 animate-spin rounded-full border-2 border-primary border-r-transparent" />
      <span>{label}</span>
    </div>
  );
}

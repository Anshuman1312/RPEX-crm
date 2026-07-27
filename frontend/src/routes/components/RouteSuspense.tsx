import { PropsWithChildren, Suspense } from "react";

export function RouteSuspense({ children }: PropsWithChildren) {
  return (
    <Suspense
      fallback={
        <div className="space-y-2">
          <div className="h-6 w-40 animate-pulse rounded bg-muted" />
          <div className="h-24 w-full animate-pulse rounded bg-muted" />
        </div>
      }
    >
      {children}
    </Suspense>
  );
}

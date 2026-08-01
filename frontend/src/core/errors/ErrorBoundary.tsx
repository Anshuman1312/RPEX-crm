import { ErrorBoundary as ReactErrorBoundary, FallbackProps, getErrorMessage } from "react-error-boundary";
import { ReactNode, ErrorInfo } from "react";

interface Props {
  children: ReactNode;
}

function ErrorFallback({ error, resetErrorBoundary }: FallbackProps) {
  const errorMessage = getErrorMessage(error);

  return (
    <div className="grid min-h-screen place-items-center bg-background p-6 text-foreground">
      <div className="max-w-lg space-y-3 text-center">
        <h1 className="text-2xl font-semibold">Something went wrong</h1>
        <p className="text-sm text-muted-foreground">
          A recoverable UI error was caught. Please refresh this page.
        </p>
        {errorMessage && (
          <pre className="mt-4 rounded bg-muted p-4 text-left text-xs overflow-auto max-h-40 max-w-full text-destructive">
            {errorMessage}
          </pre>
        )}
        <button
          onClick={resetErrorBoundary}
          className="mt-4 px-4 py-2 bg-primary text-primary-foreground rounded hover:bg-primary/90 transition-colors text-sm font-medium"
        >
          Try Again
        </button>
      </div>
    </div>
  );
}

export function ErrorBoundary({ children }: Props) {
  const handleError = (error: unknown, info: ErrorInfo) => {
    console.error("Unhandled UI error", error, info);
  };

  return (
    <ReactErrorBoundary
      FallbackComponent={ErrorFallback}
      onError={handleError}
      onReset={() => {
        window.location.reload();
      }}
    >
      {children}
    </ReactErrorBoundary>
  );
}

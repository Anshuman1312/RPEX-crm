export function ForbiddenPage() {
  return (
    <div className="grid min-h-[60vh] place-items-center">
      <div className="space-y-2 text-center">
        <h1 className="text-3xl font-semibold">403</h1>
        <p className="text-sm text-muted-foreground">You do not have permission to access this page.</p>
      </div>
    </div>
  );
}

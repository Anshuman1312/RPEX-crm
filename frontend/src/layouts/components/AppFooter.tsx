export function AppFooter() {
  return (
    <footer className="border-t px-4 py-3 text-xs text-muted-foreground lg:px-6">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p>Enterprise CRM Platform</p>
        <p>Multi-Organization Ready • {new Date().getFullYear()}</p>
      </div>
    </footer>
  );
}

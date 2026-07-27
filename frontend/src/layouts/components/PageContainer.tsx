import { PropsWithChildren } from "react";

interface PageContainerProps extends PropsWithChildren {
  title: string;
  description?: string;
  actions?: React.ReactNode;
}

export function PageContainer({ title, description, actions, children }: PageContainerProps) {
  return (
    <section className="space-y-4">
      <header className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">{title}</h1>
          {description && <p className="text-sm text-muted-foreground">{description}</p>}
        </div>
        {actions ? <div className="shrink-0">{actions}</div> : null}
      </header>
      {children}
    </section>
  );
}

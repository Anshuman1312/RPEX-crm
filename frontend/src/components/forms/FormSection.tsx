import { PropsWithChildren } from "react";

interface FormSectionProps extends PropsWithChildren {
  title: string;
  description?: string;
}

export function FormSection({ title, description, children }: FormSectionProps) {
  return (
    <section className="space-y-4 rounded-lg border bg-card p-4">
      <header className="space-y-1">
        <h3 className="text-sm font-semibold">{title}</h3>
        {description ? <p className="text-xs text-muted-foreground">{description}</p> : null}
      </header>
      {children}
    </section>
  );
}

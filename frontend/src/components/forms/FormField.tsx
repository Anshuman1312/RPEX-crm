import { PropsWithChildren } from "react";
import { cn } from "@/utils/cn";

interface FormFieldProps extends PropsWithChildren {
  id: string;
  label: string;
  error?: string;
  required?: boolean;
  description?: string;
}

export function FormField({
  id,
  label,
  error,
  required = false,
  description,
  children
}: FormFieldProps) {
  return (
    <div className="space-y-1.5">
      <label className="text-sm font-medium" htmlFor={id}>
        {label}
        {required ? <span className="ml-1 text-destructive">*</span> : null}
      </label>
      {description ? <p className="text-xs text-muted-foreground">{description}</p> : null}
      <div className={cn(error ? "[&>input]:border-destructive" : "")}>{children}</div>
      {error ? <p className="text-xs text-destructive">{error}</p> : null}
    </div>
  );
}

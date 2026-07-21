import { ReactNode } from "react";

export interface EmptyStateProps {
  title: string;
  description?: string;
  icon?: ReactNode;
}

export const EmptyState = ({ title, description, icon }: EmptyStateProps) => (
  <div className="flex items-center gap-3 py-2 px-3 text-left bg-slate-50/60 rounded-xl border border-dashed border-slate-200">
    {icon && (
      <div className="p-1.5 bg-white rounded-lg shadow-sm text-slate-400 border border-slate-100 shrink-0">
        {icon}
      </div>
    )}
    <div className="min-w-0">
      <p className="text-xs font-bold text-slate-700 truncate">{title}</p>
      {description && (
        <p className="text-[10px] text-slate-400 truncate mt-0.5">{description}</p>
      )}
    </div>
  </div>
);

export default EmptyState;

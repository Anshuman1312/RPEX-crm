import { Eye, EyeOff, SlidersHorizontal } from "lucide-react";
import { Button } from "@/components/ui/button";
import { DashboardWidgetId } from "@/features/dashboard/types/dashboard";

interface DashboardWidgetVisibilityProps {
  widgets: Array<{ id: DashboardWidgetId; label: string }>;
  isVisible: (id: DashboardWidgetId) => boolean;
  onToggle: (id: DashboardWidgetId) => void;
}

export function DashboardWidgetVisibility({
  widgets,
  isVisible,
  onToggle
}: DashboardWidgetVisibilityProps) {
  return (
    <section className="rounded-lg border bg-card p-4">
      <header className="mb-3 flex items-center gap-2">
        <SlidersHorizontal className="h-4 w-4 text-primary" />
        <h3 className="text-sm font-semibold">Widget Visibility</h3>
      </header>

      <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
        {widgets.map(widget => {
          const visible = isVisible(widget.id);
          return (
            <Button
              className="justify-between"
              key={widget.id}
              onClick={() => onToggle(widget.id)}
              size="sm"
              variant={visible ? "outline" : "ghost"}
            >
              <span className="truncate text-left text-xs">{widget.label}</span>
              {visible ? <Eye className="h-3.5 w-3.5" /> : <EyeOff className="h-3.5 w-3.5" />}
            </Button>
          );
        })}
      </div>
    </section>
  );
}

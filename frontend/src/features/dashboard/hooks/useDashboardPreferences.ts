import { useMemo, useState } from "react";
import { defaultWidgetOrder } from "@/features/dashboard/constants/dashboardMockData";
import { DashboardWidgetId } from "@/features/dashboard/types/dashboard";

const HIDDEN_WIDGETS_KEY = "rpex_dashboard_hidden_widgets";

function readHiddenWidgets(): DashboardWidgetId[] {
  const raw = localStorage.getItem(HIDDEN_WIDGETS_KEY);
  if (!raw) {
    return [];
  }

  try {
    const parsed = JSON.parse(raw) as DashboardWidgetId[];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function writeHiddenWidgets(ids: DashboardWidgetId[]) {
  localStorage.setItem(HIDDEN_WIDGETS_KEY, JSON.stringify(ids));
}

export function useDashboardPreferences() {
  const [hiddenWidgets, setHiddenWidgets] = useState<DashboardWidgetId[]>(() => readHiddenWidgets());

  const visibleWidgets = useMemo(
    () => defaultWidgetOrder.filter(widgetId => !hiddenWidgets.includes(widgetId)),
    [hiddenWidgets]
  );

  const toggleWidget = (widgetId: DashboardWidgetId) => {
    setHiddenWidgets(current => {
      const next = current.includes(widgetId)
        ? current.filter(item => item !== widgetId)
        : [...current, widgetId];
      writeHiddenWidgets(next);
      return next;
    });
  };

  const isWidgetVisible = (widgetId: DashboardWidgetId) => !hiddenWidgets.includes(widgetId);

  return {
    visibleWidgets,
    hiddenWidgets,
    isWidgetVisible,
    toggleWidget
  };
}

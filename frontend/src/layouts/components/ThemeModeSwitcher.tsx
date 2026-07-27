import { Laptop, Moon, Sun } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ThemeMode } from "@/store/uiSlice";
import { THEME_MODE_LABELS } from "@/core/theme/theme.constants";

interface ThemeModeSwitcherProps {
  mode: ThemeMode;
  resolvedMode: "light" | "dark";
  onCycleMode: () => void;
}

function ThemeIcon({ mode, resolvedMode }: Pick<ThemeModeSwitcherProps, "mode" | "resolvedMode">) {
  if (mode === "system") {
    return <Laptop className="h-4 w-4" />;
  }

  return resolvedMode === "dark" ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />;
}

export function ThemeModeSwitcher({ mode, resolvedMode, onCycleMode }: ThemeModeSwitcherProps) {
  return (
    <Button
      aria-label={`Theme mode: ${THEME_MODE_LABELS[mode]}`}
      onClick={onCycleMode}
      size="sm"
      title={`Theme mode: ${THEME_MODE_LABELS[mode]}`}
      variant="outline"
    >
      <ThemeIcon mode={mode} resolvedMode={resolvedMode} />
      <span className="ml-2 hidden text-xs sm:inline">{THEME_MODE_LABELS[mode]}</span>
    </Button>
  );
}

import { ThemeMode } from "@/store/uiSlice";

export const THEME_MODES: ThemeMode[] = ["light", "dark", "system"];

export const THEME_MODE_LABELS: Record<ThemeMode, string> = {
  light: "Light",
  dark: "Dark",
  system: "System"
};

export function getNextThemeMode(mode: ThemeMode): ThemeMode {
  const index = THEME_MODES.indexOf(mode);
  return THEME_MODES[(index + 1) % THEME_MODES.length];
}

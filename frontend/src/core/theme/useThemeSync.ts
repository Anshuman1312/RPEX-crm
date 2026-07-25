import { useEffect } from "react";
import { useAppDispatch } from "@/hooks/redux";
import { useAppSelector } from "@/hooks/redux";
import { ResolvedTheme, setResolvedTheme } from "@/store/uiSlice";

export function useThemeSync() {
  const dispatch = useAppDispatch();
  const mode = useAppSelector(state => state.ui.themeMode);

  useEffect(() => {
    const root = document.documentElement;
    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");

    const applyTheme = () => {
      const prefersDark = mediaQuery.matches;
      const resolvedMode: ResolvedTheme = mode === "system" ? (prefersDark ? "dark" : "light") : mode;

      if (resolvedMode === "dark") {
        root.classList.add("dark");
      } else {
        root.classList.remove("dark");
      }

      root.setAttribute("data-theme-mode", mode);
      root.setAttribute("data-theme-resolved", resolvedMode);
      root.style.colorScheme = resolvedMode;
      dispatch(setResolvedTheme(resolvedMode));
    };

    applyTheme();
    mediaQuery.addEventListener("change", applyTheme);

    return () => {
      mediaQuery.removeEventListener("change", applyTheme);
    };
  }, [dispatch, mode]);
}

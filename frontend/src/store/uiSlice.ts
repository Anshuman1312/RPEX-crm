import { createSlice, PayloadAction } from "@reduxjs/toolkit";

export type ThemeMode = "light" | "dark" | "system";
export type ResolvedTheme = "light" | "dark";

interface UiState {
  sidebarCollapsed: boolean;
  mobileSidebarOpen: boolean;
  themeMode: ThemeMode;
  resolvedTheme: ResolvedTheme;
  activeOrganizationId: string | null;
}

const initialState: UiState = {
  sidebarCollapsed: false,
  mobileSidebarOpen: false,
  themeMode: "system",
  resolvedTheme: "light",
  activeOrganizationId: null
};

const uiSlice = createSlice({
  name: "ui",
  initialState,
  reducers: {
    setSidebarCollapsed(state, action: PayloadAction<boolean>) {
      state.sidebarCollapsed = action.payload;
    },
    setThemeMode(state, action: PayloadAction<ThemeMode>) {
      state.themeMode = action.payload;
    },
    setResolvedTheme(state, action: PayloadAction<ResolvedTheme>) {
      state.resolvedTheme = action.payload;
    },
    setMobileSidebarOpen(state, action: PayloadAction<boolean>) {
      state.mobileSidebarOpen = action.payload;
    },
    setActiveOrganizationId(state, action: PayloadAction<string | null>) {
      state.activeOrganizationId = action.payload;
    }
  }
});

export const {
  setSidebarCollapsed,
  setThemeMode,
  setResolvedTheme,
  setMobileSidebarOpen,
  setActiveOrganizationId
} = uiSlice.actions;
export default uiSlice.reducer;

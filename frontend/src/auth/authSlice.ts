import { createSlice, PayloadAction } from "@reduxjs/toolkit";

export type RoleName = "ADMIN" | "SEO_MANAGER" | "SALES" | "ANALYST" | null;

type AuthState = {
  accessToken: string | null;
  refreshToken: string | null;
  role: RoleName;
};

const initialState: AuthState = {
  accessToken: null,
  refreshToken: null,
  role: null
};

const STORAGE_KEY = "rpex.auth.v1";

function loadStoredAuth(): AuthState {
  if (typeof window === "undefined") {
    return initialState;
  }

  const stored = window.localStorage.getItem(STORAGE_KEY);
  if (!stored) {
    return initialState;
  }

  try {
    const parsed = JSON.parse(stored) as AuthState;
    return {
      accessToken: parsed.accessToken ?? null,
      refreshToken: parsed.refreshToken ?? null,
      role: parsed.role ?? null
    };
  } catch {
    window.localStorage.removeItem(STORAGE_KEY);
    return initialState;
  }
}

function persistAuthState(state: AuthState) {
  if (typeof window === "undefined") {
    return;
  }

  if (!state.accessToken || !state.refreshToken || !state.role) {
    window.localStorage.removeItem(STORAGE_KEY);
    return;
  }

  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

const hydratedInitialState = loadStoredAuth();

const authSlice = createSlice({
  name: "auth",
  initialState: hydratedInitialState,
  reducers: {
    setTokens(state, action: PayloadAction<{ accessToken: string; refreshToken: string; role: RoleName }>) {
      state.accessToken = action.payload.accessToken;
      state.refreshToken = action.payload.refreshToken;
      state.role = action.payload.role;
      persistAuthState(state);
    },
    clearTokens(state) {
      state.accessToken = null;
      state.refreshToken = null;
      state.role = null;
      persistAuthState(state);
    }
  }
});

export const { setTokens, clearTokens } = authSlice.actions;
export default authSlice.reducer;

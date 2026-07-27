import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { UserSession } from "@/types/auth";

type AuthStatus = "unknown" | "authenticated" | "unauthenticated";

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  session: UserSession | null;
  rememberMe: boolean;
  status: AuthStatus;
}

interface CredentialsPayload {
  accessToken: string;
  refreshToken: string;
  session: UserSession;
  rememberMe: boolean;
}

const initialState: AuthState = {
  accessToken: null,
  refreshToken: null,
  session: null,
  rememberMe: true,
  status: "unknown"
};

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    hydrateSession(state, action: PayloadAction<CredentialsPayload>) {
      state.accessToken = action.payload.accessToken;
      state.refreshToken = action.payload.refreshToken;
      state.session = action.payload.session;
      state.rememberMe = action.payload.rememberMe;
      state.status = "authenticated";
    },
    setCredentials(state, action: PayloadAction<CredentialsPayload>) {
      state.accessToken = action.payload.accessToken;
      state.refreshToken = action.payload.refreshToken;
      state.session = action.payload.session;
      state.rememberMe = action.payload.rememberMe;
      state.status = "authenticated";
    },
    updateAccessToken(state, action: PayloadAction<{ accessToken: string; refreshToken?: string | null }>) {
      state.accessToken = action.payload.accessToken;
      if (action.payload.refreshToken) {
        state.refreshToken = action.payload.refreshToken;
      }
      state.status = "authenticated";
    },
    setAuthStatus(state, action: PayloadAction<AuthStatus>) {
      state.status = action.payload;
    },
    clearCredentials(state) {
      state.accessToken = null;
      state.refreshToken = null;
      state.session = null;
      state.rememberMe = true;
      state.status = "unauthenticated";
    }
  }
});

export const { hydrateSession, setCredentials, updateAccessToken, setAuthStatus, clearCredentials } = authSlice.actions;
export default authSlice.reducer;

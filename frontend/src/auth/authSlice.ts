import { createSlice, PayloadAction } from "@reduxjs/toolkit";

type RoleName = "ADMIN" | "SEO_MANAGER" | "SALES" | "ANALYST" | null;

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

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    setTokens(state, action: PayloadAction<{ accessToken: string; refreshToken: string; role: RoleName }>) {
      state.accessToken = action.payload.accessToken;
      state.refreshToken = action.payload.refreshToken;
      state.role = action.payload.role;
    },
    clearTokens(state) {
      state.accessToken = null;
      state.refreshToken = null;
      state.role = null;
    }
  }
});

export const { setTokens, clearTokens } = authSlice.actions;
export default authSlice.reducer;

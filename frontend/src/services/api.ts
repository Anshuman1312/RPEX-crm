import axios from "axios";
import { Store } from "@reduxjs/toolkit";

import { clearTokens, setTokens } from "../auth/authSlice";
import { RootState } from "../store";

const API_BASE_URL = "http://localhost:8000/api/v1";

export const api = axios.create({
  baseURL: API_BASE_URL
});

let interceptorsReady = false;
let refreshRequest: Promise<string | null> | null = null;

export function setupApiInterceptors(store: Store<RootState>) {
  if (interceptorsReady) {
    return;
  }
  interceptorsReady = true;

  api.interceptors.request.use((config) => {
    const token = store.getState().auth.accessToken;
    if (token) {
      config.headers = config.headers ?? {};
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  });

  api.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error?.config as (typeof error.config & { _retry?: boolean }) | undefined;
      const status = error?.response?.status as number | undefined;

      if (!originalRequest || status !== 401 || originalRequest._retry || String(originalRequest.url).includes("/auth/refresh")) {
        return Promise.reject(error);
      }

      const currentState = store.getState().auth;
      if (!currentState.refreshToken) {
        store.dispatch(clearTokens());
        return Promise.reject(error);
      }

      originalRequest._retry = true;

      if (!refreshRequest) {
        refreshRequest = (async () => {
          try {
            const refreshResponse = await axios.post(`${API_BASE_URL}/auth/refresh`, {
              refresh_token: currentState.refreshToken
            });
            const nextRole = (refreshResponse.data.role ?? currentState.role ?? "ANALYST") as NonNullable<RootState["auth"]["role"]>;
            store.dispatch(
              setTokens({
                accessToken: refreshResponse.data.access_token,
                refreshToken: refreshResponse.data.refresh_token,
                role: nextRole
              })
            );
            return refreshResponse.data.access_token as string;
          } catch {
            store.dispatch(clearTokens());
            return null;
          } finally {
            refreshRequest = null;
          }
        })();
      }

      const refreshedToken = await refreshRequest;
      if (!refreshedToken) {
        return Promise.reject(error);
      }

      originalRequest.headers = originalRequest.headers ?? {};
      originalRequest.headers.Authorization = `Bearer ${refreshedToken}`;
      return api.request(originalRequest);
    }
  );
}

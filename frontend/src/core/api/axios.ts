import axios, { AxiosError } from "axios";
import { env } from "@/config/env";
import { emitAuthSessionExpired } from "@/core/auth/authEvents";
import { requestTokenRefresh } from "@/features/auth/services/authLifecycle";
import { tokenStorage } from "@/core/auth/tokenStorage";

export const http = axios.create({
  baseURL: env.apiBaseUrl,
  timeout: 15000,
  withCredentials: true
});

http.interceptors.request.use(config => {
  const token = tokenStorage.getAccessToken();
  const organizationId = tokenStorage.getOrganizationId();

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  if (organizationId) {
    config.headers["X-Organization-ID"] = organizationId;
  }

  return config;
});

http.interceptors.response.use(
  response => response,
  async (error: AxiosError<{ message?: string }>) => {
    const originalRequest = error.config as typeof error.config & { _retry?: boolean };

    if (
      error.response?.status === 401 &&
      originalRequest &&
      !originalRequest._retry &&
      !originalRequest.url?.includes("/auth/refresh")
    ) {
      originalRequest._retry = true;
      const refreshed = await requestTokenRefresh();

      if (refreshed?.accessToken) {
        originalRequest.headers = originalRequest.headers ?? {};
        originalRequest.headers.Authorization = `Bearer ${refreshed.accessToken}`;
        return http(originalRequest);
      }

      tokenStorage.clearAuth();
      emitAuthSessionExpired();
    }

    return Promise.reject(error);
  }
);

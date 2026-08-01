import type { AppDispatch } from "@/app/store";
import { authHttp } from "@/core/auth/authHttp";
import {
  AUTH_SESSION_EXPIRED_EVENT,
  AUTH_TOKEN_REFRESHED_EVENT,
  emitAuthSessionExpired,
  emitAuthTokenRefreshed
} from "@/core/auth/authEvents";
import { tokenStorage } from "@/core/auth/tokenStorage";
import {
  clearCredentials,
  hydrateSession,
  setAuthStatus,
  updateAccessToken
} from "@/features/auth/store/authSlice";

interface RefreshResponse {
  access_token?: string;
  refresh_token?: string;
  accessToken?: string;
  refreshToken?: string;
}

let refreshInFlight: Promise<RefreshResponse | null> | null = null;

export function bootstrapAuthSession(dispatch: AppDispatch) {
  const storedAuth = tokenStorage.readAuth();

  if (storedAuth) {
    dispatch(hydrateSession(storedAuth));
    return;
  }

  dispatch(setAuthStatus("unauthenticated"));
}

export async function requestTokenRefresh() {
  if (refreshInFlight) {
    return refreshInFlight;
  }

  const refreshToken = tokenStorage.getRefreshToken();

  if (!refreshToken) {
    return null;
  }

  refreshInFlight = (async () => {
    try {
      const response = await authHttp.post<RefreshResponse>("/auth/refresh", {
        refresh_token: refreshToken
      });

      const newAccessToken = response.data.access_token ?? response.data.accessToken;
      const nextRefreshToken =
        response.data.refresh_token ?? response.data.refreshToken ?? refreshToken;

      if (!newAccessToken) {
        throw new Error("Missing access token in refresh response");
      }

      tokenStorage.setAccessToken(newAccessToken);
      tokenStorage.setRefreshToken(nextRefreshToken);
      emitAuthTokenRefreshed({
        accessToken: newAccessToken,
        refreshToken: nextRefreshToken
      });

      return {
        accessToken: newAccessToken,
        refreshToken: response.data.refresh_token ?? response.data.refreshToken
      };
    } catch {
      tokenStorage.clearAuth();
      emitAuthSessionExpired();
      return null;
    } finally {
      refreshInFlight = null;
    }
  })();

  return refreshInFlight;
}

export function clearAuthSession(dispatch: AppDispatch) {
  tokenStorage.clearAuth();
  dispatch(clearCredentials());
}

export function bindAuthEvents(dispatch: AppDispatch) {
  const onTokenRefreshed = (event: Event) => {
    const customEvent = event as CustomEvent<{ accessToken: string; refreshToken?: string | null }>;

    dispatch(
      updateAccessToken({
        accessToken: customEvent.detail.accessToken,
        refreshToken: customEvent.detail.refreshToken
      })
    );
  };

  const onSessionExpired = () => {
    dispatch(clearCredentials());
  };

  window.addEventListener(AUTH_TOKEN_REFRESHED_EVENT, onTokenRefreshed as EventListener);
  window.addEventListener(AUTH_SESSION_EXPIRED_EVENT, onSessionExpired);

  return () => {
    window.removeEventListener(AUTH_TOKEN_REFRESHED_EVENT, onTokenRefreshed as EventListener);
    window.removeEventListener(AUTH_SESSION_EXPIRED_EVENT, onSessionExpired);
  };
}

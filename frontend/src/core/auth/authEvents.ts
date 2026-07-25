export const AUTH_TOKEN_REFRESHED_EVENT = "rpex:auth-token-refreshed";
export const AUTH_SESSION_EXPIRED_EVENT = "rpex:auth-session-expired";

export interface AuthTokenRefreshedDetail {
  accessToken: string;
  refreshToken?: string | null;
}

export function emitAuthTokenRefreshed(detail: AuthTokenRefreshedDetail) {
  window.dispatchEvent(new CustomEvent<AuthTokenRefreshedDetail>(AUTH_TOKEN_REFRESHED_EVENT, { detail }));
}

export function emitAuthSessionExpired() {
  window.dispatchEvent(new Event(AUTH_SESSION_EXPIRED_EVENT));
}

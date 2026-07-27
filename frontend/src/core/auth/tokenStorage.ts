import { UserSession } from "@/types/auth";

const ACCESS_TOKEN_KEY = "rpex_access_token";
const REFRESH_TOKEN_KEY = "rpex_refresh_token";
const SESSION_KEY = "rpex_user_session";
const ORG_ID_KEY = "rpex_active_org_id";
const PERSISTENCE_KEY = "rpex_auth_persistence";

type AuthPersistenceMode = "local" | "session";
const COOKIE_MAX_AGE_30_DAYS = 60 * 60 * 24 * 30;

export interface PersistAuthPayload {
  accessToken: string;
  refreshToken: string;
  session: UserSession;
  rememberMe: boolean;
}

export interface StoredAuthPayload {
  accessToken: string;
  refreshToken: string;
  session: UserSession;
  rememberMe: boolean;
}

function setPersistenceMode(mode: AuthPersistenceMode) {
  localStorage.setItem(PERSISTENCE_KEY, mode);
}

function getPersistenceMode(): AuthPersistenceMode {
  const mode = localStorage.getItem(PERSISTENCE_KEY);
  return mode === "session" ? "session" : "local";
}

function getActiveStorage(): Storage {
  return getPersistenceMode() === "session" ? sessionStorage : localStorage;
}

function clearEverywhere(key: string) {
  localStorage.removeItem(key);
  sessionStorage.removeItem(key);
}

function clearAuthKeys() {
  clearCookie(ACCESS_TOKEN_KEY);
  clearCookie(REFRESH_TOKEN_KEY);
  clearEverywhere(SESSION_KEY);
}

function buildCookieAttributes(maxAgeSeconds?: number) {
  const attributes = ["Path=/", "SameSite=Lax"];

  if (maxAgeSeconds !== undefined) {
    attributes.push(`Max-Age=${maxAgeSeconds}`);
  }

  if (window.location.protocol === "https:") {
    attributes.push("Secure");
  }

  return attributes.join("; ");
}

function setCookie(name: string, value: string, maxAgeSeconds?: number) {
  const encoded = encodeURIComponent(value);
  document.cookie = `${name}=${encoded}; ${buildCookieAttributes(maxAgeSeconds)}`;
}

function getCookie(name: string): string | null {
  const token = document.cookie
    .split(";")
    .map(entry => entry.trim())
    .find(entry => entry.startsWith(`${name}=`));

  if (!token) {
    return null;
  }

  return decodeURIComponent(token.split("=").slice(1).join("="));
}

function clearCookie(name: string) {
  document.cookie = `${name}=; ${buildCookieAttributes(0)}`;
}

export const tokenStorage = {
  persistAuth(payload: PersistAuthPayload) {
    const mode: AuthPersistenceMode = payload.rememberMe ? "local" : "session";
    const storage = mode === "local" ? localStorage : sessionStorage;
    const tokenMaxAge = payload.rememberMe ? COOKIE_MAX_AGE_30_DAYS : undefined;

    setPersistenceMode(mode);
    clearAuthKeys();

    setCookie(ACCESS_TOKEN_KEY, payload.accessToken, tokenMaxAge);
    setCookie(REFRESH_TOKEN_KEY, payload.refreshToken, tokenMaxAge);
    storage.setItem(SESSION_KEY, JSON.stringify(payload.session));
  },

  readAuth(): StoredAuthPayload | null {
    const storage = getActiveStorage();
    const accessToken = getCookie(ACCESS_TOKEN_KEY);
    const refreshToken = getCookie(REFRESH_TOKEN_KEY);
    const sessionRaw = storage.getItem(SESSION_KEY);

    if (!accessToken || !refreshToken || !sessionRaw) {
      return null;
    }

    try {
      const session = JSON.parse(sessionRaw) as UserSession;
      return {
        accessToken,
        refreshToken,
        session,
        rememberMe: getPersistenceMode() === "local"
      };
    } catch {
      return null;
    }
  },

  clearAuth() {
    clearAuthKeys();
  },

  getAccessToken: () => getCookie(ACCESS_TOKEN_KEY),

  setAccessToken(token: string) {
    const maxAge = getPersistenceMode() === "local" ? COOKIE_MAX_AGE_30_DAYS : undefined;
    setCookie(ACCESS_TOKEN_KEY, token, maxAge);
  },

  getRefreshToken: () => getCookie(REFRESH_TOKEN_KEY),

  setRefreshToken(token: string) {
    const maxAge = getPersistenceMode() === "local" ? COOKIE_MAX_AGE_30_DAYS : undefined;
    setCookie(REFRESH_TOKEN_KEY, token, maxAge);
  },

  getOrganizationId: () => localStorage.getItem(ORG_ID_KEY),

  setOrganizationId(orgId: string) {
    localStorage.setItem(ORG_ID_KEY, orgId);
  },

  clearOrganizationId() {
    localStorage.removeItem(ORG_ID_KEY);
  }
};

import { rootApi } from "@/core/api/rootApi";
import { UserSession } from "@/types/auth";
import { PermissionKey, routePermissionMap } from "@/config/permissions";
import { Role } from "@/types/auth";

interface LoginRequest {
  email: string;
  password: string;
}

interface LoginResponse {
  accessToken: string;
  refreshToken: string;
  session: UserSession;
}

interface LoginResponseRaw {
  access_token: string;
  refresh_token: string;
  token_type?: string;
  role?: Role;
}

interface RefreshRequest {
  refresh_token: string;
}

interface RefreshResponse {
  accessToken: string;
  refreshToken?: string;
}

interface RefreshResponseRaw {
  access_token?: string;
  refresh_token?: string;
  accessToken?: string;
  refreshToken?: string;
}

function decodeJwtPayload(token: string): Record<string, unknown> | null {
  try {
    const payload = token.split(".")[1];
    if (!payload) {
      return null;
    }

    const normalized = payload.replace(/-/g, "+").replace(/_/g, "/");
    const decoded = atob(normalized);
    return JSON.parse(decoded) as Record<string, unknown>;
  } catch {
    return null;
  }
}

function buildSession(raw: LoginResponseRaw, email: string): UserSession {
  const payload = decodeJwtPayload(raw.access_token);
  const userId = typeof payload?.sub === "string" ? payload.sub : email;
  const role = raw.role ?? "SUPER_ADMIN";
  const allPermissions = Array.from(new Set(Object.values(routePermissionMap))) as PermissionKey[];

  return {
    userId,
    email,
    name: email.split("@")[0] ?? "User",
    role,
    permissions: allPermissions
  };
}

export const authApi = rootApi.injectEndpoints({
  endpoints: builder => ({
    login: builder.mutation<LoginResponse, LoginRequest>({
      query: credentials => ({
        url: "/auth/login",
        method: "POST",
        data: credentials
      }),
      transformResponse: (response: LoginResponseRaw, _meta, arg) => ({
        accessToken: response.access_token,
        refreshToken: response.refresh_token,
        session: buildSession(response, arg.email)
      }),
      invalidatesTags: ["Auth"]
    }),
    me: builder.query<UserSession, void>({
      query: () => ({
        url: "/auth/me",
        method: "GET"
      }),
      providesTags: ["Auth"]
    }),
    refreshToken: builder.mutation<RefreshResponse, RefreshRequest>({
      query: payload => ({
        url: "/auth/refresh",
        method: "POST",
        data: payload
      }),
      transformResponse: (response: RefreshResponseRaw) => ({
        accessToken: response.access_token ?? response.accessToken ?? "",
        refreshToken: response.refresh_token ?? response.refreshToken
      })
    }),
    logout: builder.mutation<void, void>({
      query: () => ({
        url: "/auth/logout",
        method: "POST"
      }),
      invalidatesTags: ["Auth"]
    })
  })
});

export const { useLoginMutation, useMeQuery, useRefreshTokenMutation, useLogoutMutation } = authApi;

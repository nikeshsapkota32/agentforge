import { env } from "./env";
import { clearTokens, getAccessToken, getRefreshToken, saveTokens } from "./auth";
import type { AuthTokens, ResearchSession, SessionSummary, User } from "./types";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, init: RequestInit = {}, retry = true): Promise<T> {
  const headers = new Headers(init.headers);
  headers.set("Content-Type", "application/json");
  const token = getAccessToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const res = await fetch(`${env.apiUrl}${path}`, { ...init, headers });

  if (res.status === 401 && retry && getRefreshToken()) {
    const refreshed = await tryRefresh();
    if (refreshed) return request<T>(path, init, false);
    clearTokens();
  }

  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    throw new ApiError(res.status, text || res.statusText);
  }

  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

async function tryRefresh(): Promise<boolean> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) return false;
  try {
    const res = await fetch(`${env.apiUrl}/api/v1/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    if (!res.ok) return false;
    const data = (await res.json()) as AuthTokens;
    saveTokens(data);
    return true;
  } catch {
    return false;
  }
}

export const api = {
  auth: {
    login: (email: string, password: string) =>
      request<AuthTokens>("/api/v1/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      }),
    signup: (email: string, password: string) =>
      request<AuthTokens>("/api/v1/auth/signup", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      }),
    logout: () => request<void>("/api/v1/auth/logout", { method: "DELETE" }),
    me: () => request<User>("/api/v1/auth/me"),
  },
  sessions: {
    list: () => request<SessionSummary[]>("/api/v1/sessions"),
    get: (id: string) => request<ResearchSession>(`/api/v1/sessions/${id}`),
  },
};

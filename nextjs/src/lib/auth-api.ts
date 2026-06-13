import { API_BASE_URL } from "@/config";
import type { CurrentUser, LoginPayload, RegisterPayload } from "@/types/auth";

type ApiErrorBody = {
  detail?: string;
};

async function requestJson<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    ...init,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });

  if (!response.ok) {
    let message = "Request failed";

    try {
      const body = (await response.json()) as ApiErrorBody;
      message = body.detail ?? message;
    } catch {
      message = response.statusText || message;
    }

    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export function login(payload: LoginPayload): Promise<CurrentUser> {
  return requestJson<CurrentUser>(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function register(payload: RegisterPayload): Promise<CurrentUser> {
  return requestJson<CurrentUser>(`${API_BASE_URL}/auth/register`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function fetchCurrentUser(): Promise<CurrentUser> {
  return requestJson<CurrentUser>(`${API_BASE_URL}/auth/user`);
}

export async function logout(): Promise<void> {
  await requestJson<{ message: string }>(`${API_BASE_URL}/auth/logout`, {
    method: "POST",
  });
}

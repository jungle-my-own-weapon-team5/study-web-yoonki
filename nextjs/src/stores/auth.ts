import { create } from "zustand";

import { API_BASE_URL } from "@/config";

export type CurrentUser = {
  id: number;
  email: string;
  nickname: string;
};

type AuthStore = {
  user: CurrentUser | null;
  isLoading: boolean;
  setUser: (user: CurrentUser | null) => void;
  checkAuth: () => Promise<void>;
  logout: () => Promise<void>;
};

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  isLoading: true,
  setUser: (user) => set({ user }),
  checkAuth: async () => {
    set({ isLoading: true });

    try {
      const response = await fetch(`${API_BASE_URL}/auth/user`, {
        credentials: "include",
      });

      if (!response.ok) {
        set({ user: null });
        return;
      }

      const user = await response.json();
      set({ user });
    } catch {
      set({ user: null });
    } finally {
      set({ isLoading: false });
    }
  },
  logout: async () => {
    await fetch(`${API_BASE_URL}/auth/logout`, {
      method: "POST",
      credentials: "include",
    });
    set({ user: null });
  },
}));

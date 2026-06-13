import { create } from "zustand";

import { fetchCurrentUser, logout as requestLogout } from "@/lib/auth-api";
import type { CurrentUser } from "@/types/auth";

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
      const user = await fetchCurrentUser();
      set({ user });
    } catch {
      set({ user: null });
    } finally {
      set({ isLoading: false });
    }
  },
  logout: async () => {
    try {
      await requestLogout();
    } catch {
      // Clear local auth state even if the server session is already gone.
    } finally {
      set({ user: null });
    }
  },
}));

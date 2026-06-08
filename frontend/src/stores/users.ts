import { create } from "zustand";

const useUser = create((set) => ({
    user: null,
    setUser: (user: any) => set(user)
}));
import { create } from "zustand";

const useMemosStore = create((set) => ({
    memo: '',
    setMemo: (text: string) => set({ memo: text }),
    memos: [],
    setMemos: (newMemo: string[]) =>
        set((prev: {memos: string[]}) => ({
            memos: [...prev.memos, newMemo],
        })),
}));

export default useMemosStore;
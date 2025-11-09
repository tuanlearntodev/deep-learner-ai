import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User, Workspace } from '@/lib/api';

interface AppState {
  user: User | null;
  currentWorkspace: Workspace | null;
  setUser: (user: User | null) => void;
  setCurrentWorkspace: (workspace: Workspace | null) => void;
  clearSession: () => void;
}

export const useStore = create<AppState>()(
  persist(
    (set) => ({
      user: null,
      currentWorkspace: null,
      setUser: (user) => set({ user }),
      setCurrentWorkspace: (workspace) => set({ currentWorkspace: workspace }),
      clearSession: () => set({ user: null, currentWorkspace: null }),
    }),
    {
      name: 'app-storage',
    }
  )
);

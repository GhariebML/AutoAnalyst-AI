import { create } from 'zustand';

interface AppState {
  activeTab: 'Campaigns' | 'Saved' | 'Settings' | 'Dashboard' | 'Analytics';
  activeAgent: 'content' | 'strategy' | 'research' | 'analytics' | 'design' | 'saved' | 'settings';
  currentTaskId: string | null;
  theme: 'light' | 'dark';
  setActiveTab: (tab: AppState['activeTab']) => void;
  setActiveAgent: (agent: AppState['activeAgent']) => void;
  setCurrentTaskId: (id: string | null) => void;
  toggleTheme: () => void;
}

export const useAppStore = create<AppState>((set) => ({
  activeTab: 'Campaigns',
  activeAgent: 'content',
  currentTaskId: null,
  theme: 'dark', // default to dark per premium UI constraints
  setActiveTab: (tab) => set({ activeTab: tab }),
  setActiveAgent: (agent) => set({ activeAgent: agent }),
  setCurrentTaskId: (id) => set({ currentTaskId: id }),
  toggleTheme: () => set((state) => ({ theme: state.theme === 'light' ? 'dark' : 'light' })),
}));

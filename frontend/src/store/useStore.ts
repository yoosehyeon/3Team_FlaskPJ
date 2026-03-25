import { create } from "zustand";

interface AppState {
  selectedLocation: { lat: number, lng: number } | null;
  setSelectedLocation: (loc: { lat: number, lng: number } | null) => void;
  isReportModalOpen: boolean;
  setReportModalOpen: (isOpen: boolean) => void;
  user: any | null; // Supabase user
  setUser: (user: any | null) => void;
}

export const useStore = create<AppState>((set) => ({
  selectedLocation: null,
  setSelectedLocation: (loc) => set({ selectedLocation: loc }),
  isReportModalOpen: false,
  setReportModalOpen: (isOpen) => set({ isReportModalOpen: isOpen }),
  user: null,
  setUser: (user) => set({ user }),
}));

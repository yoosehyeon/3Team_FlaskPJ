// src/store/useMapStore.js
import { create } from 'zustand';

export const useMapStore = create((set) => ({
  // 🔍 검색 상태
  searchStart: { lat: 37.2659, lng: 127.0000 },
  searchEnd: { lat: 37.2775, lng: 127.0160 },
  setSearchStart: (coords) => set({ searchStart: coords }),
  setSearchEnd: (coords) => set({ searchEnd: coords }),

  // 📡 API 응답
  rawRouteData: null,
  setRawRouteData: (data) => set({ rawRouteData: data }),

  // ⏱️ 계산된 시간
  nondisabledTime: null,
  wheelchairTime: null,
  setSafeRoute: (times) => set({
    nondisabledTime: times.nondisabled,
    wheelchairTime: times.wheelchair,
  }),

  // 🗺️ 지도용 필터된 경로
  safePolylineCoords: null,
  setSafePolylineCoords: (coords) => set({ safePolylineCoords: coords }),

  // 📊 상세 경로 정보
  routeDetails: null,
  setRouteDetails: (details) => set({ routeDetails: details }),

  // 로딩 & 에러
  isLoading: false,
  error: null,
  setIsLoading: (bool) => set({ isLoading: bool }),  // ✅ 수정: setLoading → setIsLoading
  setError: (err) => set({ error: err }),            // ✅ 추가
}));

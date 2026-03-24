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
  setIsLoading: (bool) => set({ isLoading: bool }),
  setError: (err) => set({ error: err }),

  // 🚨 [F5 김성익] 실시간 위험 마커
  dangerMarkers: [],
  addDangerMarker: (marker) =>
    set((state) => {
      // 30분 이상 된 마커 자동 소멸
      const thirtyMinutesAgo = Date.now() - 30 * 60 * 1000;
      const fresh = state.dangerMarkers.filter(
        (m) => new Date(m.created_at).getTime() > thirtyMinutesAgo
      );
      return { dangerMarkers: [...fresh, { ...marker, _addedAt: Date.now() }] };
    }),
  removeDangerMarker: (id) =>
    set((state) => ({
      dangerMarkers: state.dangerMarkers.filter((m) => m.id !== id),
    })),
  clearDangerMarkers: () => set({ dangerMarkers: [] }),
}));

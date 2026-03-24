import { create } from 'zustand';

export const useMapStore = create((set) => ({
  // 🔍 검색 상태
  searchStart: null,      // { lat, lng }
  searchEnd: null,        // { lat, lng }
  setSearchStart: (coords) => set({ searchStart: coords }),
  setSearchEnd: (coords) => set({ searchEnd: coords }),

  // 📡 API 응답 (원시)
  rawRouteData: null,     // Tmap API 응답 전체
  setRawRouteData: (data) => set({ rawRouteData: data }),

  // ⏱️ 계산된 시간 (F1에서 사용)
  nondisabledTime: null,  // 예: 420초 (비장애인)
  wheelchairTime: null,   // 예: 1600초 (휠체어)
  setSafeRoute: (times) => set({
    nondisabledTime: times.nondisabled,
    wheelchairTime: times.wheelchair,
  }),

  // 🗺️ 지도용 필터된 경로
  safePolylineCoords: null,  // Polyline용 좌표 배열: [[lat, lng], ...]
  setSafePolylineCoords: (coords) => set({ safePolylineCoords: coords }),

  // 📊 상세 경로 정보
  routeDetails: null,     // { distance, time, batteryUsage, busStops }
  setRouteDetails: (details) => set({ routeDetails: details }),

  // 로딩 & 에러
  isLoading: false,
  error: null,
  setLoading: (bool) => set({ isLoading: bool }),
  setError: (err) => set({ error: err }),
}));

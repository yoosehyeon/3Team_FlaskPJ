import { create } from 'zustand';

// create 함수를 이용해 전역 상태 창고(Store)를 만듭니다.
const useUIStore = create((set) => ({
  // --- 1. 보관할 데이터들 (State) ---

  // 출발지와 도착지 정보
  startPoint: null,
  endPoint: null,

  // 현재 지도의 중심 좌표 (기본값: 수원역)
  mapCenter: [37.2664, 127.0002],

  // 백엔드(Flask)에서 계산되어 넘어올 핵심 경로 데이터
  routeInfo: null,

  // --- 2. 데이터를 변경하는 조작 버튼들 (Actions) ---

  // 출발지/도착지 설정 함수
  setStartPoint: (point) => set({ startPoint: point }),
  setEndPoint: (point) => set({ endPoint: point }),

  // [추가됨] useSafeRoute 훅에서 통신 성공 시 호출할 함수들
  setMapCenter: (center) => set({ mapCenter: center }),
  setRouteInfo: (info) => set({ routeInfo: info }),

  // 로딩 & 에러
  isLoading: false,
  error: null,
  setIsLoading: (bool) => set({ isLoading: bool }),
  setError: (err) => set({ error: err }),

  // ⚠️ [중복 주의 — F5 김성익]
  // dangerMarkers 상태는 useMapStore.js 에 정식으로 관리됩니다.
  // DangerMarker.jsx, useReportsRealtime.js 모두 useMapStore 를 직접 참조하므로
  // 이 블록은 현재 사용되지 않습니다.
  // 추후 B팀원과 협의 후 이 블록 전체를 제거할 것을 권장합니다.
  dangerMarkers: [],
  addDangerMarker: (marker) =>
    set((state) => {
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

export default useUIStore;

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

  // 🚨 [추가] 위험 신고 모달 전역 상태
  isReportModalOpen: false,
  openReportModal: () => set({ isReportModalOpen: true }),
  closeReportModal: () => set({ isReportModalOpen: false }),

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

export default useUIStore;

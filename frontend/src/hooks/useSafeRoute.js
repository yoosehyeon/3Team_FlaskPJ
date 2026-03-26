import { useMutation } from '@tanstack/react-query';
// 수정: 우리가 맞춘 스토어 이름인 useUIStore로 가져옵니다.
import useUIStore from '../store/useUIStore';

export const useSafeRoute = () => {
  // 창고에서 데이터를 저장하는 함수를 가져옵니다.
  const setRouteInfo = useUIStore((state) => state.setRouteInfo);
  const setMapCenter = useUIStore((state) => state.setMapCenter);

  // useMutation은 '데이터를 생성/검색'하는 요청에 최적화되어 있습니다.
  return useMutation({
    // 1. 실제 백엔드와 통신하는 함수
    mutationFn: async ({ start, end }) => {
      // 수정: 비교 기능이 빠졌으므로 일반 경로 API로 요청을 보냅니다.
      const response = await fetch('/api/route', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          start_place: start,
          end_place: end,
        }),
      });

      if (!response.ok) {
        throw new Error('경로를 불러오는 데 실패했습니다.');
      }

      return response.json();
    },

    // 2. 통신 성공 시 실행될 로직
    onSuccess: (data) => {
      // 백엔드에서 준 데이터(data.path 등)를 창고에 저장
      setRouteInfo(data);

      // 검색 결과의 첫 번째 지점으로 지도의 중심을 이동시킵니다.
      if (data.path && data.path.length > 0) {
        setMapCenter(data.path[0]);
      }

      console.log("경로 탐색 성공:", data);
    },

    // 3. 통신 실패 시 실행될 로직
    onError: (error) => {
      console.error("경로 탐색 에러:", error.message);
      alert("경로를 찾을 수 없습니다. 주소를 다시 확인해주세요.");
    },
  });
};

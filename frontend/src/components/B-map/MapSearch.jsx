import React, { useState } from 'react';
import { Navigation } from 'lucide-react';
// 앞서 정리한 폴더 구조에 맞춰 useUIStore로 변경 (경로는 실제에 맞게 조절하세요)
import useUIStore from '../../store/useUIStore';
import { useSafeRoute } from '../../hooks/useSafeRoute';

export default function MapSearch() {
  const [start, setStart] = useState('');
  const [end, setEnd] = useState('');

  // 1. 전역 상태에 검색어를 저장하기 위해 스토어에서 함수 가져오기 (필요 시)
  // const setRoutePoints = useUIStore((state) => state.setRoutePoints);

  // React Query의 useMutation 훅을 사용하여 비동기 요청 함수(mutate)와 상태(isPending)를 가져옴
  const { mutate, isPending } = useSafeRoute();

  /**
   * 폼 제출 핸들러
   * @param {Event} e - Form Submit Event
   */
  const handleSearch = (e) => {
    e.preventDefault();
    if (!start || !end) return alert("출발지와 도착지를 모두 입력해주세요!");

    // (선택) 지도 컴포넌트(SafeMap) 등에서 출발/도착지 텍스트를 알아야 한다면 전역 스토어에 저장
    // setRoutePoints({ start, end });

    // 2. 비교 기능이 빠졌으므로 일반 경로 탐색 API(/api/route) 호출 용도로 사용
    mutate({ start, end });
  };

  return (
    <div className="absolute top-6 left-1/2 -translate-x-1/2 z-[1000] w-full max-w-md px-4">
      <form
        onSubmit={handleSearch}
        className="bg-white rounded-2xl shadow-2xl p-4 border border-gray-100 flex flex-col gap-3"
      >
        {/* 출발지 입력 필드 */}
        <div className="relative">
          <input
            type="text"
            placeholder="출발지 입력"
            value={start}
            onChange={(e) => setStart(e.target.value)}
            className="w-full pl-4 pr-4 py-2 bg-gray-50 rounded-lg outline-none focus:ring-2 focus:ring-blue-500 text-sm"
          />
        </div>

        {/* 도착지 입력 필드 */}
        <div className="relative">
          <input
            type="text"
            placeholder="도착지 입력"
            value={end}
            onChange={(e) => setEnd(e.target.value)}
            className="w-full pl-4 pr-4 py-2 bg-gray-50 rounded-lg outline-none focus:ring-2 focus:ring-red-500 text-sm"
          />
        </div>

        {/* API 요청 상태(isPending)에 따라 버튼 텍스트 및 활성화 상태 변경 */}
        <button
          type="submit"
          disabled={isPending}
          className={`w-full py-3 text-white rounded-xl font-bold text-sm flex items-center justify-center gap-2 transition-all ${
            isPending ? 'bg-gray-400 cursor-not-allowed' : 'bg-slate-800 hover:bg-black'
          }`}
        >
          <Navigation size={16} />
          {isPending ? '경로 계산 중...' : '안전 경로 검색'}
        </button>
      </form>
    </div>
  );
}

// MapControls.jsx (수정안)
import { useState } from 'react';
import { useMapStore } from '../../store/useMapStore';

export default function MapControls() {
  const { routeDetails } = useMapStore();
  const [showDetails, setShowDetails] = useState(false);

  if (!routeDetails) return null;

  return (
    <div
      // z-index 추가 및 이벤트 전파 방지
      className="absolute bottom-6 left-6 z-10 bg-white rounded-lg border border-gray-200 shadow-md p-4 max-w-xs"
      onPointerDown={(e) => e.stopPropagation()} // 마우스/터치 시 지도 움직임 방지
      onWheel={(e) => e.stopPropagation()}       // 휠 스크롤 시 지도 확대/축소 방지
      onClick={(e) => e.stopPropagation()}       // 클릭 이벤트가 지도로 넘어가는 것 방지
    >
      <button
        onClick={() => setShowDetails(!showDetails)}
        className="w-full px-3 py-2 bg-blue-600 text-white text-sm font-medium rounded hover:bg-blue-700"
      >
        {showDetails ? '숨기기' : '경로 상세보기'}
      </button>

      {showDetails && (
        <div className="mt-3 text-xs space-y-2">
          <p>
            <strong>거리:</strong> {(routeDetails.distance / 1000).toFixed(2)} km
          </p>
          <p>
            <strong>예상 시간:</strong> {Math.round(routeDetails.time / 60)} 분
          </p>
          <p>
            <strong>배터리 소모:</strong> {routeDetails.batteryUsage} %
          </p>
        </div>
      )}
    </div>
  );
}

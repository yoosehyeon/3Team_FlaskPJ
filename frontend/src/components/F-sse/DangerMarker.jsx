import { useMapStore } from '../../store/useMapStore';

const TYPE_LABELS = {
  stairs: '계단',
  construction: '공사 중',
  steep_slope: '급경사',
  elevator_broken: '엘리베이터 고장',
};

const SEVERITY_COLOR = {
  1: 'bg-yellow-400',
  2: 'bg-orange-400',
  3: 'bg-orange-500',
  4: 'bg-red-500',
  5: 'bg-red-700',
};

/**
 * DangerMarker — 카카오맵 위에 올라가는 위험 마커 오버레이
 * 사용법: <DangerMarker marker={markerObject} />
 */
export default function DangerMarker({ marker }) {
  const removeDangerMarker = useMapStore((s) => s.removeDangerMarker);
  const colorClass = SEVERITY_COLOR[marker.severity] || 'bg-red-500';

  return (
    <div className="relative flex flex-col items-center animate-bounce-once">
      {/* 메인 마커 아이콘 */}
      <div
        className={`w-10 h-10 rounded-full ${colorClass} flex items-center justify-center
                    shadow-lg border-2 border-white cursor-pointer
                    animate-pulse`}
        title={TYPE_LABELS[marker.barrier_type] || '위험'}
      >
        <span className="text-white text-lg font-bold">!</span>
      </div>

      {/* 툴팁 */}
      <div className="absolute bottom-12 left-1/2 -translate-x-1/2
                      bg-gray-900 text-white text-xs rounded-lg px-3 py-2
                      whitespace-nowrap shadow-xl z-50 pointer-events-none">
        <p className="font-bold">{TYPE_LABELS[marker.barrier_type] || '위험 신고'}</p>
        <p className="text-gray-300">위험도 {marker.severity}/5</p>
        {marker.image_url && (
          <img
            src={marker.image_url}
            alt="신고 이미지"
            className="mt-1 w-24 h-16 object-cover rounded"
          />
        )}
        <button
          onClick={() => removeDangerMarker(marker.id)}
          className="mt-1 text-red-400 hover:text-red-300 text-xs underline"
        >
          마커 닫기
        </button>
      </div>

      {/* 마커 꼬리 */}
      <div className={`w-0 h-0 border-l-4 border-r-4 border-t-8
                       border-l-transparent border-r-transparent
                       ${colorClass.replace('bg-', 'border-t-')}`} />
    </div>
  );
}

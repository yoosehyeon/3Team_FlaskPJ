import React, { useState, useMemo } from 'react';
import { Navigation, MapPin, Flag, Clock, Ruler } from 'lucide-react';
import useUIStore from '../../store/useUIStore';
import { useSafeRoute } from '../../hooks/useSafeRoute';

export default function MapSearch() {
  const [start, setStart] = useState('수원시청');
  const [end, setEnd] = useState('수원역');
  
  const routeInfo = useUIStore((state) => state.routeInfo);
  const { mutate, isPending } = useSafeRoute();

  // 소요 시간 및 거리 계산 (Tmap 응답 기반)
  const routeSummary = useMemo(() => {
    if (!routeInfo || !routeInfo.features || routeInfo.features.length === 0) return null;
    const props = routeInfo.features[0].properties;
    return {
      totalTime: Math.floor(props.totalTime / 60), // 초 -> 분
      totalDistance: (props.totalDistance / 1000).toFixed(1), // m -> km
      hasObstacle: routeInfo.has_obstacle
    };
  }, [routeInfo]);


  /**
   * 주소 또는 키워드를 좌표로 변환 (하이브리드 검색)
   */
  const searchCoord = (text) => {
    return new Promise((resolve, reject) => {
      const geocoder = new window.kakao.maps.services.Geocoder();
      const ps = new window.kakao.maps.services.Places();

      // 1. 먼저 도로명/지번 주소로 검색
      geocoder.addressSearch(text, (result, status) => {
        if (status === window.kakao.maps.services.Status.OK) {
          resolve({ lat: parseFloat(result[0].y), lng: parseFloat(result[0].x) });
        } else {
          // 2. 주소 검색 실패 시 키워드(지명)로 검색
          ps.keywordSearch(text, (data, psStatus) => {
            if (psStatus === window.kakao.maps.services.Status.OK) {
              resolve({ lat: parseFloat(data[0].y), lng: parseFloat(data[0].x) });
            } else {
              reject(new Error(`'${text}' 장소를 찾을 수 없습니다.`));
            }
          });
        }
      });
    });
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!start || !end) return alert("출발지와 도착지를 모두 입력해주세요!");

    if (!window.kakao || !window.kakao.maps || !window.kakao.maps.services) {
      return alert("지도 서비스를 불러오는 중입니다. 잠시만 기다려주세요.");
    }

    try {
      const startCoord = await searchCoord(start);
      const endCoord = await searchCoord(end);
      
      // 백엔드 API 호출 (Tmap 경로)
      mutate({ start: startCoord, end: endCoord });
    } catch (err) {
      alert(err.message);
    }
  };

  return (
    <div className="absolute top-6 left-6 z-[1000] w-full max-w-sm flex flex-col gap-4">
      {/* 검색 폼 */}
      <form
        onSubmit={handleSearch}
        className="bg-white/95 backdrop-blur-md rounded-3xl shadow-2xl p-6 border border-white/20 flex flex-col gap-4"
      >
        <div className="flex flex-col gap-3 relative">
          <div className="absolute left-3 top-1/2 -translate-y-1/2 w-0.5 h-8 bg-gray-100 left-[18px] z-0" />
          
          <div className="relative z-10 flex items-center gap-3">
            <div className="w-9 h-9 rounded-full bg-blue-50 flex items-center justify-center text-blue-600 shadow-sm border border-blue-100">
              <MapPin size={18} />
            </div>
            <input
              type="text"
              placeholder="출발지 (예: 수원시청)"
              value={start}
              onChange={(e) => setStart(e.target.value)}
              className="flex-1 h-11 px-4 bg-gray-50 border-none rounded-xl text-sm focus:ring-2 focus:ring-blue-500 transition-all font-medium"
            />
          </div>

          <div className="relative z-10 flex items-center gap-3">
            <div className="w-9 h-9 rounded-full bg-red-50 flex items-center justify-center text-red-600 shadow-sm border border-red-100">
              <Flag size={18} />
            </div>
            <input
              type="text"
              placeholder="도착지 (예: 수원역)"
              value={end}
              onChange={(e) => setEnd(e.target.value)}
              className="flex-1 h-11 px-4 bg-gray-50 border-none rounded-xl text-sm focus:ring-2 focus:ring-red-500 transition-all font-medium"
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={isPending}
          className={`w-full h-14 text-white rounded-2xl font-bold text-base flex items-center justify-center gap-2 shadow-lg transition-all transform active:scale-95 ${
            isPending ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700 hover:shadow-blue-200'
          }`}
        >
          {isPending ? (
            <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
          ) : (
            <Navigation size={20} fill="currentColor" />
          )}
          {isPending ? '경로 계산 중...' : '안전 경로 검색'}
        </button>
      </form>

      {/* 결과 카드 */}
      {routeSummary && (
        <div className="bg-white/95 backdrop-blur-md rounded-3xl shadow-2xl p-6 border border-white/20 animate-in fade-in slide-in-from-top-4 duration-500">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-bold text-gray-900">예상 소요 시간</h3>
            {routeSummary.hasObstacle && (
              <span className="px-2 py-1 bg-amber-50 text-amber-600 text-[10px] font-bold rounded-lg border border-amber-100">
                주의: 계단 포함
              </span>
            )}
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div className="flex items-center gap-3 p-3 bg-blue-50 rounded-2xl border border-blue-100">
              <div className="text-blue-600"><Clock size={20} /></div>
              <div>
                <p className="text-[10px] text-blue-500 font-bold uppercase">Time</p>
                <p className="text-xl font-black text-blue-700 leading-none">{routeSummary.totalTime}<span className="text-sm">분</span></p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-2xl border border-gray-100">
              <div className="text-gray-400"><Ruler size={20} /></div>
              <div>
                <p className="text-[10px] text-gray-400 font-bold uppercase">Distance</p>
                <p className="text-xl font-black text-gray-700 leading-none">{routeSummary.totalDistance}<span className="text-sm">km</span></p>
              </div>
            </div>
          </div>
          
          <p className="mt-4 text-xs text-gray-400 font-medium leading-relaxed">
            * 휠체어 평균 속도(4km/h) 기준 예상 시간입니다. 실시간 상황에 따라 다를 수 있습니다.
          </p>
        </div>
      )}
    </div>
  );
}

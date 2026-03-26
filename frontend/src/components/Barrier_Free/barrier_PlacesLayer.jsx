import React from 'react';
import { Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import useUIStore from '../../store/useUIStore';
import { useBarrierPlaces } from '../../hooks/barrier_usePlaces';

/**
 * BarrierPlacesLayer
 * 지도 중심 300m 이내의 무장애 편의시설을 조회하여 마커로 표시합니다.
 */
const BarrierPlacesLayer = () => {
  const mapCenter = useUIStore((state) => state.mapCenter);
  const places = useUIStore((state) => state.barrierPlaces);
  
  // 좌표 정규화 ([lat, lng] 대응)
  const lat = Array.isArray(mapCenter) ? mapCenter[0] : (mapCenter?.lat || 37.2664);
  const lng = Array.isArray(mapCenter) ? mapCenter[1] : (mapCenter?.lng || 127.0002);

  // 1. 커스텀 훅을 사용하여 데이터 페칭 (mapCenter가 바뀔 때마다 실행됨)
  useBarrierPlaces(lat, lng);

  // 2. 카테고리에 따른 마커 아이콘 설정
  const getIcon = (category) => {
    const isIndoor = category.includes('실내');
    return new L.DivIcon({
      html: `
        <div class="flex items-center justify-center w-10 h-10 rounded-full border-4 border-white shadow-lg ${isIndoor ? 'bg-indigo-600' : 'bg-emerald-600'} text-white">
          ${isIndoor ? '🏛️' : '🌳'}
        </div>
      `,
      className: 'bg-transparent',
      iconSize: [40, 40],
      iconAnchor: [20, 20],
      popupAnchor: [0, -20],
    });
  };

  return (
    <>
      {places && places.map((place) => (
        <Marker 
          key={place.esntl_id} 
          position={[place.lat, place.lng]}
          icon={getIcon(place.category_mid)}
        >
          <Popup className="barrier-popup">
            <div className="p-3 max-w-[200px] rounded-xl overflow-hidden">
              <div className="flex items-center gap-2 mb-2">
                <span className={`px-2 py-0.5 text-[10px] font-bold rounded-full text-white ${place.category_mid.includes('실내') ? 'bg-indigo-500' : 'bg-emerald-500'}`}>
                  {place.category_mid.includes('실내') ? '실내' : '실외'}
                </span>
                <span className="text-[10px] font-medium text-gray-400">#무장애장소</span>
              </div>
              
              <h3 className="font-extrabold text-[#111827] text-sm mb-1 leading-tight">
                {place.name}
              </h3>
              
              <p className="text-[#6B7280] text-[11px] mb-3 leading-relaxed">
                {place.address}
              </p>
              
              <div className="flex items-center justify-between pt-2 border-t border-gray-100">
                <span className="text-[10px] text-gray-400">내 위치에서</span>
                <span className="text-xs font-bold text-[#4F46E5]">{place.distance}m</span>
              </div>
            </div>
          </Popup>
        </Marker>
      ))}
    </>
  );
};

export default BarrierPlacesLayer;

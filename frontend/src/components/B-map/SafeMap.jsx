import React, { useEffect } from 'react';
import { MapContainer, TileLayer, useMap, Polyline } from 'react-leaflet';
import L from 'leaflet'; // Leaflet 직접 참조 추가
import 'leaflet/dist/leaflet.css';
import useUIStore from '../../store/useUIStore';
import BarrierFacilityMarkers from '../../pages/Barrier_Free/barrier_FacilityMarkers';

// --- Leaflet 기본 아이콘 경로 설정 (아이콘 깨짐 방지) ---
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconUrl: markerIcon,
  iconRetinaUrl: markerIcon2x,
  shadowUrl: markerShadow,
});

/**
 * 지도의 중심 좌표나 줌 레벨이 바뀔 때 실제 지도를 움직여주는 헬퍼 컴포넌트
 */
function MapController({ center, zoom }) {
  const map = useMap();
  useEffect(() => {
    if (center) {
      map.setView(center, zoom);
    }
  }, [center, zoom, map]);
  return null;
}

/**
 * SafeMap 컴포넌트
 * 기본 내보내기(default export)가 정확히 명시되어 있습니다.
 */
const SafeMap = () => {
  // 상태 창고(useUIStore)에서 데이터 가져오기
  const mapCenter = useUIStore((state) => state.mapCenter);
  const routeInfo = useUIStore((state) => state.routeInfo);
  const defaultZoom = 15;

  return (
    <div className="w-full h-full relative">
      <MapContainer
        center={mapCenter}
        zoom={defaultZoom}
        className="w-full h-full z-0"
        scrollWheelZoom={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* 중심 좌표가 바뀌면 지도를 이동시킵니다 */}
        <MapController center={mapCenter} zoom={defaultZoom} />

        {/* 300m 반경 무장애 (실내/실외) 편의 시설 & 관광지 표시 컴포넌트 */}
        <BarrierFacilityMarkers />

        {/* 경로 데이터(routeInfo.path)가 존재할 때만 지도 위에 파란색 선을 그립니다 */}
        {routeInfo && routeInfo.path && routeInfo.path.length > 0 && (
          <Polyline
            positions={routeInfo.path}
            pathOptions={{ color: '#3b82f6', weight: 6, opacity: 0.8 }}
          />
        )}
      </MapContainer>
    </div>
  );
};

export default SafeMap; // 명시적 기본 내보내기

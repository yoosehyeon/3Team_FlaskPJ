// SafeMap.js 수정안 (Bounds 적용)
import { useState, useEffect, useMemo } from 'react';
import { Map, MapMarker } from 'react-kakao-maps-sdk';
import { useMapStore } from '../../store/useMapStore';
import RoutePolyline from './RoutePolyline';
import MapControls from './MapControls';

export default function SafeMap() {
  const { searchStart, searchEnd, safePolylineCoords, isLoading, error } = useMapStore();
  const [map, setMap] = useState(null); // 지도 객체 상태 저장

  // 경로 좌표가 변경될 때마다 화면 영역(Bounds) 재계산
  const bounds = useMemo(() => {
    if (!safePolylineCoords || safePolylineCoords.length === 0) return null;

    const bounds = new window.kakao.maps.LatLngBounds();
    safePolylineCoords.forEach(([lat, lng]) => {
      bounds.extend(new window.kakao.maps.LatLng(lat, lng));
    });
    return bounds;
  }, [safePolylineCoords]);

  // 계산된 영역으로 지도 시점 이동
  useEffect(() => {
    if (map && bounds) {
      map.setBounds(bounds);
    }
  }, [map, bounds]);

  if (isLoading) return <div className="p-6 text-center">경로 계산 중...</div>;
  if (error) return <div className="p-6 text-red-600">오류: {error}</div>;

  const center = searchStart || { lat: 37.265, lng: 127.002 };

  return (
    <div className="w-full h-96 rounded-lg overflow-hidden border border-gray-200">
      <Map
        center={center}
        level={5}
        className="w-full h-full"
        onCreate={setMap} // 생성된 지도 객체를 상태에 저장
      >
        {searchStart && <MapMarker position={searchStart} title="출발지" />}
        {searchEnd && <MapMarker position={searchEnd} title="도착지" />}
        {safePolylineCoords && <RoutePolyline coords={safePolylineCoords} />}
        <MapControls />
      </Map>
    </div>
  );
}

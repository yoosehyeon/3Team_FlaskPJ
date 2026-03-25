import React from 'react';
import SafeMap from '../components/B-map/SafeMap';
import MapSearch from '../components/B-map/MapSearch';

export default function MapPage() {
  return (
    // 전체 화면을 꽉 채우도록 설정 (100vh)
    <div className="relative w-full h-screen overflow-hidden bg-gray-100">

      {/* 1. 상단 플로팅 검색창 */}
      <MapSearch />

      {/* 2. 전체 화면을 채우는 지도 도화지 (경로선 포함) */}
      <SafeMap />

    </div>
  );
}

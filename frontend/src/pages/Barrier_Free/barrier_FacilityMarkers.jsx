import React, { useEffect, useState } from 'react';
import { Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import axios from 'axios';
import useUIStore from '../../store/useUIStore';

// 실내시설 아이콘 (파란색 계열)
const indoorIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

// 실외시설 아이콘 (녹색 계열)
const outdoorIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

const BarrierFacilityMarkers = () => {
  const mapCenter = useUIStore((state) => state.mapCenter);
  const [facilities, setFacilities] = useState([]);

  useEffect(() => {
    const fetchFacilities = async () => {
      if (!mapCenter) return;
      
      try {
        const [lat, lng] = mapCenter;
        
        // VITE_API_URL 환경변수 또는 localhost:5000 사용
        const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:5000';
        
        const response = await axios.get(`${baseUrl}/api/places`, {
          params: {
            lat,
            lng,
            radius: 300 // 반경 300m
          }
        });
        
        if (response.data && response.data.status === 'success') {
          setFacilities(response.data.data);
        }
      } catch (error) {
        console.error('Failed to fetch barrier-free facilities:', error);
      }
    };
    
    fetchFacilities();
  }, [mapCenter]); // 중심 좌표가 변경될 때마다 300m 반경 시설 재검색

  return (
    <>
      {facilities.map((facility) => {
        // GeoJSON 문자열에서 좌표 추출. (ST_AsGeoJSON 반환 형태)
        // location = '{"type":"Point","coordinates":[lng, lat]}'
        if (!facility.location) return null;
        
        let position = null;
        try {
          const locObj = JSON.parse(facility.location);
          if (locObj.coordinates) {
            position = [locObj.coordinates[1], locObj.coordinates[0]]; // [lat, lng]
          }
        } catch (e) {
          return null;
        }

        if (!position) return null;

        const isIndoor = facility.meta && facility.meta.type === 'indoor';
        const iconToUse = isIndoor ? indoorIcon : outdoorIcon;

        return (
          <Marker key={facility.id} position={position} icon={iconToUse}>
            <Popup>
              <div className="text-sm">
                <h3 className="font-bold text-lg mb-1">{facility.name}</h3>
                <p className="text-gray-600 mb-1">{facility.category}</p>
                {facility.meta && facility.meta.mlsfc && (
                  <p className="text-gray-600 text-xs mb-1">상세 분류: {facility.meta.mlsfc}</p>
                )}
                <p className="text-gray-500 text-xs">{facility.address}</p>
                <div className="mt-2 text-xs font-semibold text-blue-600">
                  {isIndoor ? '실내 무장애 시설' : '실외 관광/편의 시설'}
                </div>
              </div>
            </Popup>
          </Marker>
        );
      })}
    </>
  );
};

export default BarrierFacilityMarkers;

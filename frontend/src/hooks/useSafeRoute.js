// src/hooks/useSafeRoute.js
import { useEffect } from 'react';
import { useMapStore } from '../store/useMapStore';  // ✅ 이 줄 추가!

// 1️⃣ T-map API 호출 함수
export const fetchTmapRoute = async ({ start, end }) => {
  if (!start || !end) return null;

  const TMAP_API_KEY = import.meta.env.VITE_TMAP_API_KEY;
  const url = `https://apis.openapi.sk.com/tmap/routes/pedestrian?version=1&format=json`;

  const body = {
    startX: start.lng,
    startY: start.lat,
    endX: end.lng,
    endY: end.lat,
    reqCoordType: 'WGS84GEO',
    resCoordType: 'WGS84GEO',
    startName: 'start',
    endName: 'end',
  };

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'appKey': TMAP_API_KEY,
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) throw new Error(`Tmap API error: ${response.status}`);
  return response.json();
};

// 2️⃣ useSafeRoute 훅
export const useSafeRoute = () => {
  const {
    searchStart,
    searchEnd,
    setSafePolylineCoords,
    setError,
    setIsLoading
  } = useMapStore();

  useEffect(() => {
    const getRoute = async () => {
      console.log('🟢 useSafeRoute 시작', { searchStart, searchEnd });

      if (!searchStart || !searchEnd) {
        console.log('⚠️ 출발지/도착지 없음');
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        console.log('🔵 T-map API 호출 중...');
        const data = await fetchTmapRoute({ start: searchStart, end: searchEnd });
        console.log('🟡 전체 API 응답:', data);

        if (data.features && data.features.length > 0) {
          const geometry = data.features[0].geometry;
          let coords = [];

          if (geometry.type === 'LineString') {
            coords = geometry.coordinates.map(([lng, lat]) => [lat, lng]);
          } else if (geometry.type === 'MultiLineString') {
            coords = geometry.coordinates.flat().map(([lng, lat]) => [lat, lng]);
          }

          console.log('🟠 추출된 좌표:', coords);
          setSafePolylineCoords(coords);
        }
      } catch (err) {
        console.error('🔴 에러 발생:', err);
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    getRoute();
  }, [searchStart, searchEnd, setSafePolylineCoords, setError, setIsLoading]);
};

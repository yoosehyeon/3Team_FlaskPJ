import React, { useEffect, useRef, useState } from 'react';
import useUIStore from '../store/useUIStore';
import MapSearch from '../components/B-map/MapSearch';
import { usePlaces } from '../hooks/usePlaces';
import { useElevators } from '../hooks/useElevators';
import { useReportsRealtime } from '../hooks/useReportsRealtime';

const MapPage = () => {
    const mapContainer = useRef(null);
    const [map, setMap] = useState(null);
    const [center, setCenter] = useState({ lat: 37.2635727, lng: 127.0287149 });
    
    // Zustand Store
    const routeInfo = useUIStore((state) => state.routeInfo);
    const polylineRef = useRef(null);

    const { data: placesData } = usePlaces(center.lat, center.lng);
    const { data: elevatorsData } = useElevators();
    useReportsRealtime();

    // 2. 지도 초기화
    useEffect(() => {
        const apiKey = import.meta.env.VITE_KAKAO_APP_KEY;
        const scriptId = 'kakao-maps-sdk';

        const initMap = () => {
            if (!window.kakao || !window.kakao.maps) return;
            window.kakao.maps.load(() => {
                const options = {
                    center: new window.kakao.maps.LatLng(center.lat, center.lng),
                    level: 3
                };
                const kakaoMap = new window.kakao.maps.Map(mapContainer.current, options);
                setMap(kakaoMap);
                const zoomControl = new window.kakao.maps.ZoomControl();
                kakaoMap.addControl(zoomControl, window.kakao.maps.ControlPosition.RIGHT);
            });
        };

        if (window.kakao && window.kakao.maps) {
            initMap();
        } else {
            if (!document.getElementById(scriptId)) {
                const script = document.createElement('script');
                script.id = scriptId;
                script.src = `https://dapi.kakao.com/v2/maps/sdk.js?appkey=${apiKey}&libraries=services,clusterer&autoload=false`;
                script.async = true;
                script.onload = initMap;
                document.head.appendChild(script);
            }
        }
    }, []);

    // 3. Tmap 경로 그리기 (Polyline)
    useEffect(() => {
        if (!map || !routeInfo || !routeInfo.features) return;

        // 기존 경로 삭제
        if (polylineRef.current) {
            polylineRef.current.setMap(null);
        }

        const path = [];
        routeInfo.features.forEach(feature => {
            if (feature.geometry.type === "LineString") {
                feature.geometry.coordinates.forEach(coord => {
                    // Tmap [lng, lat] -> Kakao [lat, lng]
                    path.push(new window.kakao.maps.LatLng(coord[1], coord[0]));
                });
            }
        });

        if (path.length > 0) {
            const polyline = new window.kakao.maps.Polyline({
                path: path,
                strokeWeight: 6,
                strokeColor: '#3b82f6',
                strokeOpacity: 0.8,
                strokeStyle: 'solid'
            });

            polyline.setMap(map);
            polylineRef.current = polyline;

            // 지도 중심 이동 및 확대 레벨 조정
            map.setCenter(path[0]);
            map.setLevel(4);
        }
    }, [map, routeInfo]);

    // 4. 배리어프리 마커
    useEffect(() => {
        if (!map || !placesData) return;
        const clusterer = new window.kakao.maps.MarkerClusterer({
            map: map,
            averageCenter: true,
            minLevel: 5
        });
        const markers = (placesData.features || []).map(feature => {
            const [lng, lat] = feature.geometry.coordinates;
            return new window.kakao.maps.Marker({
                position: new window.kakao.maps.LatLng(lat, lng),
                title: feature.properties.name
            });
        });
        clusterer.addMarkers(markers);
        return () => clusterer.clear();
    }, [map, placesData]);

    // 5. 엘리베이터 마커
    useEffect(() => {
        if (!map || !elevatorsData) return;
        (elevatorsData.elevators || []).forEach(elevator => {
            const [lng, lat] = elevator.coordinates;
            new window.kakao.maps.Marker({
                position: new window.kakao.maps.LatLng(lat, lng),
                map: map,
                title: `${elevator.name} (${elevator.status})`
            });
        });
    }, [map, elevatorsData]);

    return (
        <div className="relative w-full h-screen bg-gray-100">
            <MapSearch />
            <div 
                ref={mapContainer}
                className="w-full h-full"
                style={{ height: '100vh' }}
            />
        </div>
    );
};

export default MapPage;

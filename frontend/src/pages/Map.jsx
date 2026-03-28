import React, { useEffect, useState } from 'react';
import { Map, MapMarker, MarkerClusterer, Polyline, ZoomControl, useKakaoLoader, CustomOverlayMap } from 'react-kakao-maps-sdk';
import { ShieldAlert, Loader2, X, Info } from 'lucide-react';

import useUIStore from '../store/useUIStore';
import useMapStore from '../store/useMapStore';

import MapSearch from '../components/B-map/MapSearch';
import ReportModal from '../components/F-sse/ReportModal';
import DangerMarker from '../components/F-sse/DangerMarker';

import { usePlaces } from '../hooks/usePlaces';
import { useElevators } from '../hooks/useElevators';
import { useReportsRealtime } from '../hooks/useReportsRealtime';
import api from '../lib/api';

const MapPage = () => {
    // 1. 카카오 지도 SDK 로드 (PRD 4.2 안정성 확보)
    const [loading] = useKakaoLoader({
        appkey: import.meta.env.VITE_KAKAO_APP_KEY,
        libraries: ["services", "clusterer"],
    });

    const [center, setCenter] = useState({ lat: 37.2635727, lng: 127.0287149 });
    const [selectedElevator, setSelectedElevator] = useState(null);

    // Zustand Stores
    const routeInfo = useUIStore((state) => state.routeInfo);
    const { isReportModalOpen, openReportModal, closeReportModal } = useUIStore();
    const { dangerMarkers, setDangerMarkers, cleanupOldMarkers, removeDangerMarker } = useMapStore();

    // Data Hooks
    const { data: placesData } = usePlaces(center.lat, center.lng);
    const { data: elevatorsData } = useElevators();
    useReportsRealtime();

    // 2. 초기 신고 데이터 페칭 및 자동 소멸 타이머
    useEffect(() => {
        if (loading) return;

        const fetchInitialReports = async () => {
            try {
                const { data } = await api.get('/api/reports');
                if (data.reports) setDangerMarkers(data.reports);
            } catch (err) {
                console.error("Failed to fetch reports:", err);
            }
        };
        fetchInitialReports();

        // 1분마다 오래된 마커 청소 (PRD 3.4)
        const timer = setInterval(() => {
            cleanupOldMarkers();
        }, 60000);

        return () => clearInterval(timer);
    }, [loading, setDangerMarkers, cleanupOldMarkers]);

    // 3. 통합 경로 시각화 엔진 (PRD 4.2: 구간별 색상 및 마커 최적화)
    const routeLayers = React.useMemo(() => {
        if (!routeInfo) return [];
        const layers = [];

        // CASE 1: 대중교통 데이터 (steps 기반)
        if (routeInfo.steps) {
            routeInfo.steps.forEach((step, idx) => {
                const path = [];
                if (step.path && Array.isArray(step.path)) {
                    step.path.forEach(coord => {
                        path.push({ lat: coord.lat, lng: coord.lng });
                    });
                }

                if (path.length > 0) {
                    let color = "#F59E0B"; // 휠체어/도보 이동 (어텐션을 끄는 주황색)
                    let style = 'shortdot'; // 아주 촘촘한 점선으로 변경 (두꺼운 ---- 느낌 제거)
                    let weight = 5;
                    
                    if (step.type === 1) {
                        color = "#10B981"; // 지하철 (에메랄드 그린)
                        style = 'solid';
                        weight = 8;
                    } else if (step.type === 2) {
                        color = "#6366F1"; // 버스 (인디고 보라)
                        style = 'solid';
                        weight = 8; // 대중교통은 굵게
                    }

                    layers.push({
                        id: `step-${idx}`,
                        path,
                        color,
                        style,
                        weight,
                        type: step.type,
                        busNo: step.busNo,
                        startName: step.startName
                    });
                }
            });
            return layers;
        }

        // CASE 2: Tmap 휠체어 전용 데이터 (features 기반)
        if (routeInfo.features) {
            const path = [];
            routeInfo.features.forEach(feature => {
                if (feature.geometry.type === "LineString") {
                    feature.geometry.coordinates.forEach(coord => {
                        path.push({ lat: coord[1], lng: coord[0] });
                    });
                }
            });
            
            if (path.length > 0) {
                // 장애물 유무에 따른 색상 분기 (PRD 3.1)
                const color = routeInfo.has_obstacle ? "#f97316" : "#3b82f6";
                layers.push({ id: 'wheelchair-path', path, color, style: 'solid', weight: 8 });
            }
            return layers;
        }

        return [];
    }, [routeInfo]);

    // 4. 경로 검색 시 지도 영역 자동 조정 (PRD 4.1)
    const [map, setMap] = useState(null);
    useEffect(() => {
        if (!map || routeLayers.length === 0) return;
        const bounds = new window.kakao.maps.LatLngBounds();
        routeLayers.forEach(layer => {
            layer.path.forEach(p => bounds.extend(new window.kakao.maps.LatLng(p.lat, p.lng)));
        });
        map.setBounds(bounds, 80); // padding 80px
    }, [map, routeLayers]);

    if (loading) {
        return (
            <div className="w-full h-screen bg-white flex flex-col items-center justify-center gap-4">
                <Loader2 className="w-12 h-12 text-blue-600 animate-spin" />
                <p className="font-bold text-gray-600">회장님, 수원시 정밀 지도를 불러오고 있습니다...</p>
            </div>
        );
    }

    return (
        <div className="relative w-full h-screen bg-gray-100 overflow-hidden">
            <MapSearch />

            <button
                onClick={openReportModal}
                className="absolute bottom-10 right-6 z-[1000] flex items-center gap-2 px-6 py-4 bg-red-600 hover:bg-red-700 text-white rounded-full shadow-2xl transition-all transform hover:scale-105 active:scale-95 font-bold group"
            >
                <ShieldAlert size={20} className="group-hover:animate-pulse" />
                <span>위험 신고</span>
                <div className="flex items-center justify-center min-w-[20px] h-5 px-1.5 bg-white/20 rounded-full text-[10px]">
                    {dangerMarkers.length}
                </div>
            </button>

            <Map
                center={center}
                className="w-full h-full"
                level={3}
                onCreate={setMap}
                onIdle={(map) => {
                    const latlng = map.getCenter();
                    setCenter({ lat: latlng.getLat(), lng: latlng.getLng() });
                }}
            >
                <ZoomControl position="RIGHT" />

                {/* 경로 레이어 렌더링 (구간별 색상 차별화) */}
                {routeLayers.map((layer) => (
                    <React.Fragment key={layer.id}>
                        <Polyline
                            path={layer.path}
                            strokeWeight={layer.weight}
                            strokeColor={layer.color}
                            strokeOpacity={1.0}
                            strokeStyle={layer.style}
                        />
                        {/* 버스/지하철 탑승/하차 지점 아이콘 */}
                        {(layer.type === 1 || layer.type === 2) && (
                            <>
                                <CustomOverlayMap position={layer.path[0]} yAnchor={1}>
                                    <div className={`px-2.5 py-1 rounded-md shadow-xl border-2 border-white text-[11px] font-extrabold text-white mb-2 ${layer.type === 1 ? 'bg-green-600' : 'bg-indigo-600'}`}>
                                        {layer.type === 1 ? '지하철 승차' : `${layer.busNo}번 승차`}
                                    </div>
                                </CustomOverlayMap>
                                <CustomOverlayMap position={layer.path[layer.path.length - 1]} yAnchor={1}>
                                    <div className="px-2.5 py-1 rounded-md shadow-lg border-2 border-white text-[11px] font-extrabold text-white mb-2 bg-slate-700">
                                        하차
                                    </div>
                                </CustomOverlayMap>
                            </>
                        )}
                    </React.Fragment>
                ))}

                {/* 출발/도착 마커 (항상 최상단) */}
                {routeLayers.length > 0 && (
                    <>
                        <CustomOverlayMap position={routeLayers[0].path[0]} yAnchor={1.1}>
                            <div className="relative flex flex-col items-center">
                                <div className="w-12 h-12 bg-blue-600 rounded-full shadow-2xl border-2 border-white flex items-center justify-center z-10 animate-bounce">
                                    <span className="text-white text-[12px] font-black leading-none">출발</span>
                                </div>
                                <div className="w-0 h-0 border-l-[8px] border-l-transparent border-r-[8px] border-r-transparent border-t-[12px] border-t-blue-600 mt-[-2px] drop-shadow-lg"></div>
                            </div>
                        </CustomOverlayMap>

                        <CustomOverlayMap 
                            position={routeLayers[routeLayers.length - 1].path[routeLayers[routeLayers.length - 1].path.length - 1]} 
                            yAnchor={1.1}
                        >
                            <div className="relative flex flex-col items-center">
                                <div className="w-12 h-12 bg-red-600 rounded-full shadow-2xl border-2 border-white flex items-center justify-center z-10">
                                    <span className="text-white text-[12px] font-black leading-none">도착</span>
                                </div>
                                <div className="w-0 h-0 border-l-[8px] border-l-transparent border-r-[8px] border-r-transparent border-t-[12px] border-t-red-600 mt-[-2px] drop-shadow-lg"></div>
                            </div>
                        </CustomOverlayMap>
                    </>
                )}

                {/* 배리어프리 베뉴 (클러스터러) */}
                <MarkerClusterer averageCenter={true} minLevel={5}>
                    {placesData?.features?.map((f, i) => (
                        <MapMarker
                            key={`place-${i}`}
                            position={{ lat: f.geometry.coordinates[1], lng: f.geometry.coordinates[0] }}
                            title={f.properties.name}
                        />
                    ))}
                </MarkerClusterer>

                {/* 엘리베이터 마커 (PRD 3.2: 이미지 깨짐 방지를 위한 텍스트 오버레이 마커) */}
                {elevatorsData?.elevators?.map((e, i) => {
                    const isNormal = e.status === '정상' || e.status === 'normal';
                    return (
                        <React.Fragment key={`ev-group-${i}`}>
                            <CustomOverlayMap position={{ lat: e.coordinates[0], lng: e.coordinates[1] }}>
                                <div
                                    onClick={() => setSelectedElevator(e)}
                                    className={`w-10 h-10 rounded-full flex items-center justify-center border-2 border-white shadow-xl cursor-pointer transition-transform hover:scale-110 active:scale-95 ${isNormal ? 'bg-green-500' : 'bg-red-500'
                                        }`}
                                >
                                    <span className="text-[10px] font-bold text-white leading-none">
                                        {isNormal ? '정상' : '점검'}
                                    </span>
                                </div>
                            </CustomOverlayMap>

                            {/* 상세 정보 팝업 (클릭 시 노출) */}
                            {selectedElevator?.id === e.id && (
                                <CustomOverlayMap position={{ lat: e.coordinates[0], lng: e.coordinates[1] }} yAnchor={1.6}>
                                    <div className="bg-white rounded-2xl shadow-2xl border border-gray-100 p-4 min-w-[210px] animate-in zoom-in-95 duration-200 z-[1002]">
                                        <div className="flex justify-between items-start mb-3">
                                            <div>
                                                <h4 className="text-sm font-bold text-gray-900">{e.station_name}역</h4>
                                                <span className="text-[10px] text-blue-600 font-semibold bg-blue-50 px-1.5 py-0.5 rounded">{e.line}</span>
                                            </div>
                                            <button onClick={() => setSelectedElevator(null)} className="p-1 hover:bg-gray-100 rounded-full transition-colors">
                                                <X size={14} className="text-gray-400" />
                                            </button>
                                        </div>
                                        <div className="space-y-2">
                                            <div className="flex items-start gap-2 text-[11px] text-gray-600 leading-tight">
                                                <Info size={12} className="mt-0.5 flex-shrink-0" />
                                                <span>{e.location}</span>
                                            </div>
                                            <div className={`text-[10px] font-bold px-2.5 py-1 rounded-full inline-flex items-center gap-1 ${isNormal ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'}`}>
                                                <div className={`w-1.5 h-1.5 rounded-full ${isNormal ? 'bg-green-500' : 'bg-red-500'}`} />
                                                상태: {e.status}
                                            </div>
                                        </div>
                                        <div className="absolute bottom-[-8px] left-1/2 -translate-x-1/2 w-4 h-4 bg-white rotate-45 border-r border-b border-gray-100"></div>
                                    </div>
                                </CustomOverlayMap>
                            )}
                        </React.Fragment>
                    );
                })}

                {/* 실시간 위험 신고 마커 (F5 엔진 핵심) */}
                {dangerMarkers.map((m) => (
                    <DangerMarker
                        key={m.id}
                        marker={m}
                        onRemove={removeDangerMarker}
                    />
                ))}
            </Map>

            {/* 4. 신고 모달 (PRD 3.1) */}
            <ReportModal
                isOpen={isReportModalOpen}
                onClose={closeReportModal}
                lat={center.lat}
                lng={center.lng}
            />
        </div>
    );
};

export default MapPage;

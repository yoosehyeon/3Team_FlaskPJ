import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Navigation, MapPin, Flag, Clock, Ruler, Bus, ArrowLeft, ChevronDown, ChevronUp } from 'lucide-react';
import useUIStore from '../../store/useUIStore';
import { useSafeRoute } from '../../hooks/useSafeRoute';
import { useTransit } from '../../hooks/useTransit';

export default function MapSearch() {
  const navigate = useNavigate();
  const [start, setStart] = useState('수원시청');
  const [end, setEnd] = useState('수원역');
  const [selectedMode, setSelectedMode] = useState('wheelchair');
  const [isCollapsed, setIsCollapsed] = useState(false); // 접기 상태 추가

  // 스토어 상태
  const { wheelchairInfo, transitInfo, setRouteInfo } = useUIStore();

  // [추가] 경로 데이터 변경 시 지도 자동 동기화
  React.useEffect(() => {
    if (selectedMode === 'wheelchair' && wheelchairInfo) {
      setRouteInfo(wheelchairInfo);
    } else if (selectedMode === 'transit' && transitInfo) {
      setRouteInfo(transitInfo);
    }
  }, [wheelchairInfo, transitInfo, selectedMode, setRouteInfo]);
  
  // 훅 초기화
  const wheelchairMutation = useSafeRoute();
  const transitMutation = useTransit();
  const isPending = wheelchairMutation.isPending || transitMutation.isPending;

  // 1. 휠체어 경로 요약 계산
  const wheelchairSummary = useMemo(() => {
    if (!wheelchairInfo || !wheelchairInfo.features || wheelchairInfo.features.length === 0) return null;
    const props = wheelchairInfo.features[0].properties;
    return {
      time: Math.floor(props.totalTime / 60),
      distance: (props.totalDistance / 1000).toFixed(1),
    };
  }, [wheelchairInfo]);

  // 2. 대중교통 경로 요약 계산
  const transitSummary = useMemo(() => {
    if (!transitInfo) return null;
    return {
      time: transitInfo.totalTime,
      distance: (transitInfo.totalDistance / 1000).toFixed(1),
    };
  }, [transitInfo]);

  const searchCoord = (text) => {
    return new Promise((resolve, reject) => {
      const geocoder = new window.kakao.maps.services.Geocoder();
      const ps = new window.kakao.maps.services.Places();
      geocoder.addressSearch(text, (result, status) => {
        if (status === window.kakao.maps.services.Status.OK) {
          resolve({ lat: parseFloat(result[0].y), lng: parseFloat(result[0].x) });
        } else {
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
    if (!window.kakao?.maps?.services) return alert("지도 서비스 준비 중...");

    try {
      const startCoord = await searchCoord(start);
      const endCoord = await searchCoord(end);
      
      wheelchairMutation.mutate({ start: startCoord, end: endCoord });
      transitMutation.mutate({ 
        startX: startCoord.lng, startY: startCoord.lat, 
        endX: endCoord.lng, endY: endCoord.lat 
      });
      
      setSelectedMode('wheelchair');
    } catch (err) {
      alert(err.message);
    }
  };

  const selectMode = (mode) => {
    setSelectedMode(mode);
    if (mode === 'wheelchair' && wheelchairInfo) setRouteInfo(wheelchairInfo);
    if (mode === 'transit' && transitInfo) setRouteInfo(transitInfo);
  };

  return (
    <div className="absolute top-6 left-6 z-[1000] flex flex-col gap-4 transition-all duration-500 ease-in-out">
      {/* 상단 컨트롤 바 (뒤로가기 & 접기) */}
      <div className="flex gap-2">
        <button 
          onClick={() => navigate('/')}
          className="w-12 h-12 bg-white/95 backdrop-blur-md rounded-2xl shadow-xl flex items-center justify-center text-gray-700 hover:bg-gray-50 transition-all border border-white/20"
        >
          <ArrowLeft size={20} strokeWidth={2.5} />
        </button>
        <button 
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="w-12 h-12 bg-white/95 backdrop-blur-md rounded-2xl shadow-xl flex items-center justify-center text-blue-600 hover:bg-blue-50 border border-white/20"
        >
          {isCollapsed ? <ChevronDown size={20} strokeWidth={2.5} /> : <ChevronUp size={20} strokeWidth={2.5} />}
        </button>
      </div>

      {/* 검색 패널 (고정 너비 380px 설정으로 모드 전환 시 너비 변동 방지) */}
      <div className={`flex flex-col gap-4 w-[380px] ${isCollapsed ? 'hidden' : 'block'}`}>
        <form onSubmit={handleSearch} className="bg-white/95 backdrop-blur-md rounded-3xl shadow-2xl p-6 border border-white/20">
          <div className="flex flex-col gap-3 mb-4">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-full bg-blue-50 flex items-center justify-center text-blue-600"><MapPin size={18} /></div>
              <input type="text" placeholder="출발지" value={start} onChange={(e) => setStart(e.target.value)} className="flex-1 h-11 px-4 bg-gray-50 rounded-xl text-sm" />
            </div>
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-full bg-red-50 flex items-center justify-center text-red-600"><Flag size={18} /></div>
              <input type="text" placeholder="도착지" value={end} onChange={(e) => setEnd(e.target.value)} className="flex-1 h-11 px-4 bg-gray-50 rounded-xl text-sm" />
            </div>
          </div>
          <button type="submit" disabled={isPending} className="w-full h-14 bg-blue-600 text-white rounded-2xl font-bold flex items-center justify-center gap-2 shadow-lg">
            {isPending ? '계산 중...' : '안전 경로 검색'}
          </button>
        </form>

        {(wheelchairSummary || transitSummary) && (
          <div className="bg-white/95 backdrop-blur-8 rounded-3xl shadow-2xl border border-white/20 flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-300">
            <div className="grid grid-cols-2 p-2 gap-2 bg-gray-50">
              <button 
                onClick={() => selectMode('wheelchair')}
                className={`p-4 rounded-2xl transition-all text-left ${selectedMode === 'wheelchair' ? 'bg-blue-600 shadow-lg text-white' : 'bg-white border-gray-100 border text-gray-900'}`}
              >
                <p className={`text-[10px] font-bold uppercase mb-1 ${selectedMode === 'wheelchair' ? 'text-blue-100' : 'text-blue-600'}`}>휠체어 소요시간</p>
                <div className="flex items-baseline gap-1">
                  <span className="text-2xl font-black">{wheelchairSummary?.time || '--'}</span>
                  <span className="text-xs font-bold opacity-70">분</span>
                  {wheelchairSummary && (
                    <span className={`ml-auto text-xs font-bold ${selectedMode === 'wheelchair' ? 'text-white' : 'text-blue-600'}`}>
                      {wheelchairSummary.distance}km
                    </span>
                  )}
                </div>
              </button>
              <button 
                onClick={() => selectMode('transit')}
                className={`p-4 rounded-2xl transition-all text-left ${selectedMode === 'transit' ? 'bg-indigo-600 shadow-lg text-white' : 'bg-white border-gray-100 border text-gray-900'}`}
              >
                <p className={`text-[10px] font-bold uppercase mb-1 ${selectedMode === 'transit' ? 'text-indigo-100' : 'text-indigo-600'}`}>저상버스 소요시간</p>
                <div className="flex items-baseline gap-1">
                  <span className="text-2xl font-black">{transitSummary?.time || '--'}</span>
                  <span className="text-xs font-bold opacity-70">분</span>
                  {transitSummary && (
                    <span className={`ml-auto text-xs font-bold ${selectedMode === 'transit' ? 'text-white' : 'text-indigo-600'}`}>
                      {transitSummary.distance}km
                    </span>
                  )}
                </div>
              </button>
            </div>

            <div className="p-6">
              {selectedMode === 'wheelchair' ? (
                <div className="space-y-4">
                  <div className="flex items-center gap-2 text-blue-600">
                    <Clock size={16} />
                    <span className="text-sm font-bold">휠체어 전문 도보 경로</span>
                  </div>
                  <div className="p-4 bg-blue-50 rounded-2xl text-blue-700 text-xs font-medium leading-relaxed border border-blue-100">
                    "계단과 가파른 경사를 피하여 휠체어 사용자가 이동할 수 있는 경로입니다."
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="flex items-center gap-2 text-indigo-600">
                    <Bus size={16} />
                    <span className="text-sm font-bold">대중교통 상세 경로</span>
                  </div>
                  <div className="space-y-2 max-h-[45vh] overflow-y-auto overscroll-contain pr-2 pb-6" style={{ pointerEvents: 'auto' }}>
                    {transitInfo?.message && (!transitInfo?.steps || transitInfo.steps.length === 0) ? (
                      <div className="p-4 bg-indigo-50 rounded-2xl text-indigo-700 text-xs font-medium leading-relaxed border border-indigo-100 text-center">
                        🚨 {transitInfo.message}
                      </div>
                    ) : (
                    <div className="flex flex-col gap-3 relative">
                        {/* 세로 타임라인 굵은 선 (디자인 개선) */}
                        <div className="absolute left-[20px] top-6 bottom-6 w-0.5 bg-indigo-100 z-0 opacity-60"></div>
                        
                        {transitInfo?.steps.map((s, i) => (
                          <div key={i} className="flex items-start gap-4 p-4 bg-white hover:bg-slate-50 transition-all duration-200 rounded-2xl border border-slate-100 shadow-[0_4px_12px_rgba(0,0,0,0.03)] relative z-10 group">
                            {s.type === 3 ? (
                              <>
                                <div className="mt-0.5 w-[42px] h-[42px] rounded-full bg-orange-50 flex items-center justify-center text-orange-500 border-4 border-white shadow-md shrink-0 transition-transform group-hover:scale-110">
                                  <Ruler size={16} strokeWidth={2.5} />
                                </div>
                                <div className="flex flex-col w-full">
                                  <span className="text-sm font-black text-slate-800 tracking-tight leading-tight">
                                    {s.summary || (i === 0 ? '출발지 ➔ 승차 정류장' : (i === transitInfo.steps.length - 1 ? '하차 정류장 ➔ 도착지' : '도보 이동'))}
                                  </span>
                                  <div className="flex items-center gap-2 mt-1.5 font-bold">
                                    <span className="text-[11px] px-2 py-0.5 bg-orange-100 text-orange-600 rounded-md shadow-sm">
                                      약 {Math.ceil(s.distance / 60)}분
                                    </span>
                                    <span className="text-[11px] text-slate-400 font-medium">({s.distance}m)</span>
                                  </div>
                                </div>
                              </>
                            ) : (
                              <>
                                <div className={`mt-0.5 w-[42px] h-[42px] rounded-full flex items-center justify-center text-white border-4 border-white shadow-lg shrink-0 transition-transform group-hover:scale-110 ${s.type === 1 ? 'bg-emerald-500' : 'bg-indigo-600'}`}>
                                  {s.type === 1 ? <Navigation size={16} strokeWidth={2.5}/> : <Bus size={16} strokeWidth={2.5}/>}
                                </div>
                                <div className="flex flex-col w-full">
                                  <div className="flex items-center justify-between mb-2">
                                    <span className={`text-sm font-black tracking-tight ${s.type === 1 ? 'text-emerald-700' : 'text-indigo-900'}`}>
                                      {s.type === 1 ? '지하철' : s.busNo}
                                    </span>
                                    {s.type === 2 && (
                                      <div className="flex items-center gap-1.5">
                                        {s.isLowFloor && (
                                          <span className="text-[10px] font-black px-2 py-0.5 bg-indigo-600 text-white rounded-md shadow-sm animate-pulse">
                                            저상
                                          </span>
                                        )}
                                        {s.predictTime ? (
                                          <span className="text-[10px] font-black px-2 py-0.5 bg-red-500 text-white rounded-md shadow-sm">
                                            {s.predictTime}분 후 도착
                                          </span>
                                        ) : (
                                          <span className="text-[10px] font-bold px-2 py-0.5 bg-slate-100 text-slate-500 rounded-md">
                                            운행 정보 없음
                                          </span>
                                        )}
                                      </div>
                                    )}
                                  </div>
                                  
                                  <div className="flex flex-col gap-2 p-3 bg-slate-50/50 rounded-xl border border-slate-100/80">
                                    <div className="flex items-start gap-3">
                                      <div className="w-2.5 h-2.5 rounded-full bg-blue-500 mt-1 border-2 border-white shadow-sm ring-2 ring-blue-100"></div>
                                      <span className="text-xs text-slate-700 leading-tight">
                                        <strong className="text-slate-900 font-extrabold">{s.startName}</strong> 승차
                                      </span>
                                    </div>
                                    <div className="w-0.5 h-3 bg-slate-200 ml-[4px]"></div>
                                    <div className="flex items-start gap-3">
                                      <div className="w-2.5 h-2.5 rounded-full bg-red-500 mt-1 border-2 border-white shadow-sm ring-2 ring-red-100"></div>
                                      <span className="text-xs text-slate-700 leading-tight">
                                        <strong className="text-slate-900 font-extrabold">{s.endName}</strong> 하차
                                      </span>
                                    </div>
                                  </div>
                                  
                                  <p className="mt-2 text-[11px] text-slate-400 font-bold px-1 italic">
                                    {s.summary}
                                  </p>
                                </div>
                              </>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

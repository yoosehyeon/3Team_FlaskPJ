import React, { useEffect, useRef } from "react";
import { useQuery } from "@tanstack/react-query";
import { supabase } from "../lib/supabase";

export default function Home() {
  const mapRef = useRef<HTMLDivElement>(null);
  const kakaoMapInstance = useRef<any>(null);

  // 헬스체크 조회 (캐싱을 이용해 백엔드가 연결되었는지 확인)
  const { data: health } = useQuery({
    queryKey: ["health"],
    queryFn: async () => {
      const res = await fetch("/api/health");
      return res.json();
    },
    staleTime: 5 * 60 * 1000,
  });

  useEffect(() => {
    if (typeof window !== "undefined" && window.kakao) {
      window.kakao.maps.load(() => {
        if (!mapRef.current) return;
        
        // 수원시 권선구청 근처 중심 좌표 (예시)
        const options = {
          center: new window.kakao.maps.LatLng(37.2635727, 127.0286009),
          level: 3,
        };
        
        kakaoMapInstance.current = new window.kakao.maps.Map(mapRef.current, options);
      });
    }
  }, []);

  return (
    <div className="w-full h-full absolute inset-0">
      <div 
        ref={mapRef} 
        style={{ width: "100%", height: "100%" }} 
      />
      {health?.status === "ok" && (
        <div className="absolute top-4 left-4 bg-white/80 backdrop-blur-sm p-3 rounded-xl shadow-lg border border-slate-200 z-10">
          <h1 className="text-sm font-bold text-teal-600">수원시 휠체어 내비게이션</h1>
          <p className="text-xs text-slate-500 mt-1">서버 및 DB 연결 완료</p>
        </div>
      )}
    </div>
  );
}

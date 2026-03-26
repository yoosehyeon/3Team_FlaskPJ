import { useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { supabase } from '../lib/supabaseClient';
import { useMapStore } from '../store/useMapStore';

/**
 * F5 실시간 위험 신고 엔진 — Supabase Realtime WebSocket
 *
 * reports 테이블에 INSERT 이벤트가 발생하면 두 가지 동작을 수행합니다.
 *   1) TanStack Query ['reports'] 캐시 무효화 → GET /api/reports 재요청
 *   2) useMapStore.addDangerMarker() 호출 → 카카오맵에 마커 즉시 표시
 *      (재요청 결과를 기다리지 않고 Realtime payload 로 즉각 반영)
 *
 * PRD v3.0 / 김성익 PL 담당
 */
export function useReportsRealtime() {
  const qc = useQueryClient();
  // dangerMarkers 는 useMapStore 에서 단일 관리 (useUIStore 중복 블록은 미사용)
  const addDangerMarker = useMapStore((s) => s.addDangerMarker);

  useEffect(() => {
    const channel = supabase
      .channel('reports-changes')
      .on(
        'postgres_changes',
        { event: 'INSERT', schema: 'public', table: 'reports' },
        (payload) => {
          // 1) 전체 목록 캐시 갱신 (GET /api/reports 재요청)
          qc.invalidateQueries({ queryKey: ['reports'] });
          // 2) Realtime payload 의 신규 행을 즉시 지도 마커로 추가
          //    payload.new 에는 INSERT 된 reports 행 전체가 담겨 있음
          if (payload.new) {
            addDangerMarker(payload.new);
          }
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [qc, addDangerMarker]);
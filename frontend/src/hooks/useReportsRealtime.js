import { useEffect } from "react";
import { supabase } from "../lib/supabase";
import { useQueryClient } from "@tanstack/react-query";

/**
 * useReportsRealtime Hook
 * Supabase Realtime(WebSocket)을 통해 실시간으로 신고 데이터를 갱신합니다. (PRD 9.3)
 */
export function useReportsRealtime() {
  const queryClient = useQueryClient();

  useEffect(() => {
    // reports 테이블의 INSERT 이벤트를 감시
    const channel = supabase
      .channel("reports-changes")
      .on(
        "postgres_changes",
        { event: "INSERT", schema: "public", table: "reports" },
        (payload) => {
          console.log("New report received:", payload);
          // TanStack Query 캐시를 무효화하여 자동 리프레시 유도
          queryClient.invalidateQueries({ queryKey: ["reports"] });
        }
      )
      .subscribe();

    // cleanup: 컴포넌트 언마운트 시 채널 연결 해제 
    return () => {
      supabase.removeChannel(channel);
    };
  }, [queryClient]);
}

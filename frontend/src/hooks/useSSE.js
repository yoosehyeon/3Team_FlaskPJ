import { useEffect, useRef } from 'react';
import { useMapStore } from '../store/useMapStore';

const SSE_URL = `${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/sse`;

export function useSSE() {
  const addDangerMarker = useMapStore((s) => s.addDangerMarker);
  const esRef = useRef(null);

  useEffect(() => {
    function connect() {
      const es = new EventSource(SSE_URL);
      esRef.current = es;

      es.onopen = () => {
        console.log('[SSE] 연결 성공');
      };

      es.onmessage = (e) => {
        try {
          const data = JSON.parse(e.data);
          if (data.type === 'new_barrier') {
            addDangerMarker(data.payload);
            // 알림음 재생 시도
            try {
              const audio = new Audio('/sounds/alert.mp3');
              audio.volume = 0.5;
              audio.play().catch(() => {});
            } catch (_) {}
          }
        } catch (err) {
          console.warn('[SSE] 메시지 파싱 오류:', err);
        }
      };

      es.onerror = () => {
        console.warn('[SSE] 연결 끊김, 3초 후 재연결 시도...');
        es.close();
        setTimeout(connect, 3000);
      };
    }

    connect();

    return () => {
      if (esRef.current) {
        esRef.current.close();
      }
    };
  }, [addDangerMarker]);
}

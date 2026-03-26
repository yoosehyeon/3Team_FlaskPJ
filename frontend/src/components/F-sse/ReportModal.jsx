import { useState, useRef } from 'react';

// 백엔드 API 기본 URL (환경변수 미설정 시 로컬 개발 서버 사용)
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

// 신고 가능한 위험 유형 목록 — PRD reports.type 컬럼 enum 값과 일치
const BARRIER_TYPES = [
  { value: 'stairs', label: '계단' },
  { value: 'construction', label: '공사 중' },
  { value: 'steep_slope', label: '급경사' },
  { value: 'elevator_broken', label: '엘리베이터 고장' },
];

/**
 * ReportModal — 위험 신고 모달 컴포넌트
 *
 * Props:
 *   - isOpen       : boolean      — 모달 표시 여부
 *   - onClose      : () => void   — 모달 닫기 콜백
 *   - userLocation : { lat, lng } — 현재 사용자 GPS 좌표
 *
 * 동작 흐름:
 *   1) 사용자가 위험 유형·위험도·사진을 선택
 *   2) POST /api/report (multipart/form-data) 호출
 *   3) 백엔드에서 Supabase Storage 업로드 + reports 테이블 INSERT
 *   4) Supabase Realtime이 INSERT를 감지 → 모든 접속자 지도에 마커 표시
 */
export default function ReportModal({ isOpen, onClose, userLocation }) {
  const [type, setType] = useState('stairs');           // 선택된 위험 유형
  const [severity, setSeverity] = useState(3);          // 위험도 (1~5)
  const [imageFile, setImageFile] = useState(null);     // 첨부 이미지 파일 객체
  const [preview, setPreview] = useState(null);         // 이미지 미리보기 URL
  const [isSubmitting, setIsSubmitting] = useState(false); // 전송 중 상태
  const [submitted, setSubmitted] = useState(false);    // 전송 완료 상태
  const fileRef = useRef(null);                         // 숨겨진 file input 참조

  // 모달이 닫혀있으면 렌더링하지 않음
  if (!isOpen) return null;

  // 이미지 파일 선택 시 미리보기 URL 생성
  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setImageFile(file);
    setPreview(URL.createObjectURL(file));
  };

  const handleSubmit = async () => {
    // GPS 위치 없으면 제출 불가
    if (!userLocation) {
      alert('현재 위치를 확인할 수 없습니다.');
      return;
    }

    setIsSubmitting(true);
    try {
      // multipart/form-data 구성 — 이미지 + 텍스트 데이터 통합 전송
      // 백엔드(reports.py)에서 이미지 업로드 + DB INSERT를 한번에 처리
      const formData = new FormData();
      formData.append('latitude', userLocation.lat);
      formData.append('longitude', userLocation.lng);
      formData.append('type', type);
      formData.append('severity', severity);
      if (imageFile) {
        formData.append('image', imageFile);  // 이미지 첨부 (선택)
      }

      // PRD v3.0 엔드포인트: POST /api/report (multipart/form-data)
      const res = await fetch(`${API_URL}/api/report`, {
        method: 'POST',
        headers: {
          // JWT 토큰 — Supabase Auth 로그인 후 발급된 토큰
          Authorization: `Bearer ${localStorage.getItem('sb_access_token') || ''}`,
        },
        body: formData,
      });

      if (res.ok) {
        // 전송 성공 → 완료 메시지 표시 후 1.5초 뒤 모달 닫기
        setSubmitted(true);
        setTimeout(() => {
          setSubmitted(false);
          setImageFile(null);
          setPreview(null);
          setType('stairs');
          setSeverity(3);
          onClose();
        }, 1500);
      } else {
        const err = await res.json();
        alert(`신고 실패: ${err.error || '알 수 없는 오류'}`);
      }
    } catch (err) {
      console.error('신고 실패:', err);
      alert('신고 전송에 실패했습니다. 다시 시도해주세요.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    // 배경 오버레이 — 클릭 시 모달 닫기
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/50"
         onClick={onClose}>
      {/* 모달 본체 — 클릭 이벤트 버블링 차단 */}
      <div
        className="w-full max-w-lg bg-white rounded-t-2xl p-6 space-y-4 animate-slide-up"
        onClick={(e) => e.stopPropagation()}
      >
        {/* 헤더 */}
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-gray-900">🚨 위험 신고</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-2xl">×</button>
        </div>

        {submitted ? (
          // 전송 완료 화면
          <div className="text-center py-8">
            <p className="text-4xl mb-2">✅</p>
            <p className="text-green-600 font-bold text-lg">신고가 접수되었습니다!</p>
            <p className="text-gray-500 text-sm">모든 사용자에게 전파 중...</p>
          </div>
        ) : (
          <>
            {/* 위험 유형 선택 — 2x2 그리드 버튼 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">위험 유형</label>
              <div className="grid grid-cols-2 gap-2">
                {BARRIER_TYPES.map((t) => (
                  <button
                    key={t.value}
                    onClick={() => setType(t.value)}
                    className={`py-2 px-3 rounded-lg border text-sm font-medium transition-colors
                      ${type === t.value
                        ? 'bg-red-500 border-red-500 text-white'
                        : 'bg-white border-gray-300 text-gray-700 hover:border-red-300'
                      }`}
                  >
                    {t.label}
                  </button>
                ))}
              </div>
            </div>

            {/* 위험도 슬라이더 (1~5) */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                위험도: <span className="text-red-500 font-bold">{severity}/5</span>
              </label>
              <input
                type="range"
                min={1}
                max={5}
                value={severity}
                onChange={(e) => setSeverity(Number(e.target.value))}
                className="w-full accent-red-500"
              />
              <div className="flex justify-between text-xs text-gray-400">
                <span>낮음</span>
                <span>높음</span>
              </div>
            </div>

            {/* 사진 업로드 — 클릭 시 파일 선택 창 열기 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">사진 첨부 (선택)</label>
              <div
                onClick={() => fileRef.current.click()}
                className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center cursor-pointer hover:border-red-300 transition-colors"
              >
                {preview ? (
                  // 이미지 미리보기
                  <img src={preview} alt="미리보기" className="max-h-32 mx-auto rounded object-cover" />
                ) : (
                  <div className="text-gray-400 text-sm">
                    <p className="text-2xl mb-1">📷</p>
                    <p>클릭하여 사진 선택</p>
                  </div>
                )}
              </div>
              {/* 숨겨진 file input — 위 div 클릭 시 프로그래밍적으로 열림 */}
              <input
                ref={fileRef}
                type="file"
                accept="image/*"
                className="hidden"
                onChange={handleImageChange}
              />
            </div>

            {/* 제출 버튼 */}
            <button
              onClick={handleSubmit}
              disabled={isSubmitting}
              className="w-full py-3 bg-red-500 hover:bg-red-600 disabled:bg-gray-300
                         text-white font-bold rounded-xl transition-colors"
            >
              {isSubmitting ? '신고 전송 중...' : '신고하기'}
            </button>
          </>
        )}
      </div>
    </div>
  );
}
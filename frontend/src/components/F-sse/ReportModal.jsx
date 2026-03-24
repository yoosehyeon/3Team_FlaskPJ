import { useState, useRef } from 'react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

const BARRIER_TYPES = [
  { value: 'stairs', label: '계단' },
  { value: 'construction', label: '공사 중' },
  { value: 'steep_slope', label: '급경사' },
  { value: 'elevator_broken', label: '엘리베이터 고장' },
];

/**
 * ReportModal — 위험 신고 모달
 * Props:
 *   - isOpen: boolean
 *   - onClose: () => void
 *   - userLocation: { lat, lng } | null
 */
export default function ReportModal({ isOpen, onClose, userLocation }) {
  const [type, setType] = useState('stairs');
  const [severity, setSeverity] = useState(3);
  const [imageFile, setImageFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const fileRef = useRef(null);

  if (!isOpen) return null;

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setImageFile(file);
    setPreview(URL.createObjectURL(file));
  };

  const handleSubmit = async () => {
    if (!userLocation) {
      alert('현재 위치를 확인할 수 없습니다.');
      return;
    }

    setIsSubmitting(true);
    try {
      let imageUrl = null;

      // 이미지가 있으면 Supabase Storage에 업로드
      if (imageFile) {
        const formData = new FormData();
        formData.append('file', imageFile);
        const uploadRes = await fetch(`${API_URL}/api/barriers/upload`, {
          method: 'POST',
          body: formData,
        });
        if (uploadRes.ok) {
          const uploadData = await uploadRes.json();
          imageUrl = uploadData.url;
        }
      }

      // 신고 데이터 전송 → SSE broadcast 트리거
      const res = await fetch(`${API_URL}/api/barriers`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          latitude: userLocation.lat,
          longitude: userLocation.lng,
          type,
          severity,
          image_url: imageUrl,
        }),
      });

      if (res.ok) {
        setSubmitted(true);
        setTimeout(() => {
          setSubmitted(false);
          setImageFile(null);
          setPreview(null);
          setType('stairs');
          setSeverity(3);
          onClose();
        }, 1500);
      }
    } catch (err) {
      console.error('신고 실패:', err);
      alert('신고 전송에 실패했습니다. 다시 시도해주세요.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/50"
         onClick={onClose}>
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
          <div className="text-center py-8">
            <p className="text-4xl mb-2">✅</p>
            <p className="text-green-600 font-bold text-lg">신고가 접수되었습니다!</p>
            <p className="text-gray-500 text-sm">모든 사용자에게 전파 중...</p>
          </div>
        ) : (
          <>
            {/* 위험 유형 선택 */}
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

            {/* 위험도 슬라이더 */}
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

            {/* 사진 업로드 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">사진 첨부 (선택)</label>
              <div
                onClick={() => fileRef.current?.click()}
                className="border-2 border-dashed border-gray-300 rounded-lg p-4
                           flex flex-col items-center justify-center cursor-pointer
                           hover:border-red-400 transition-colors"
              >
                {preview ? (
                  <img src={preview} alt="미리보기" className="w-full h-32 object-cover rounded-lg" />
                ) : (
                  <>
                    <span className="text-3xl">📷</span>
                    <span className="text-sm text-gray-500 mt-1">탭하여 사진 추가</span>
                  </>
                )}
              </div>
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
              className="w-full py-3 bg-red-500 text-white font-bold rounded-xl
                         hover:bg-red-600 disabled:opacity-50 disabled:cursor-not-allowed
                         transition-colors text-lg"
            >
              {isSubmitting ? '전송 중...' : '🚨 모두에게 알리기'}
            </button>
          </>
        )}
      </div>
    </div>
  );
}

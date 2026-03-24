import { useState } from 'react';
// 🚨 주의: SafeMap과 GapDashboard 파일이 있는 경로에 맞게 아래 import 경로를 수정해 주세요!
import SafeMap from './components/B-map/SafeMap';
import GapDashboard from './components/F1-dashboard/GapDashboard';

export default function App() {
  // 현재 어떤 화면을 보여줄지 결정하는 상태 ('home' 또는 'map')
  const [currentView, setCurrentView] = useState('home');

  return (
    <div className="min-h-screen bg-bg-light text-text-primary p-8 flex flex-col items-center justify-center space-y-4">
      {/* 제목 클릭 시 언제든 메인 홈으로 돌아오도록 설정 */}
      <h1
        className="text-4xl font-bold text-primary-main cursor-pointer"
        onClick={() => setCurrentView('home')}
      >
        모두의 길 (Modu-Gil)
      </h1>

      {currentView === 'home' ? (
        // 🏠 1. 홈 화면 (초기 화면)
        <>
          <p className="text-lg text-text-secondary">휠체어 통합 내비게이션 프론트엔드 인프라 구동 완료 🎉</p>
          <div className="flex gap-4 mt-6">
            {/* 안전 경로 버튼: 클릭하면 currentView를 'map'으로 변경 */}
            <button
              onClick={() => setCurrentView('map')}
              className="w-24 h-24 rounded-base bg-safety-cyan flex items-center justify-center text-white shadow-card transition-all duration-fast hover:scale-105 cursor-pointer"
            >
              안전 경로
            </button>
            <div className="w-24 h-24 rounded-base bg-danger-red flex items-center justify-center text-white shadow-card transition-all duration-fast hover:scale-105">
              위험 신고
            </div>
            <div className="w-24 h-24 rounded-base bg-warning-yellow flex items-center justify-center text-white shadow-card transition-all duration-fast hover:scale-105">
              수리 중
            </div>
            <div className="w-24 h-24 rounded-base bg-success-green flex items-center justify-center text-white shadow-card transition-all duration-fast hover:scale-105">
              배리어프리
            </div>
          </div>
        </>
      ) : (
        // 🗺️ 2. 지도 화면 (안전 경로 클릭 시)
        <div className="w-full max-w-5xl flex flex-col gap-6 w-full animate-fade-in">
          <button
            onClick={() => setCurrentView('home')}
            className="self-start px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 font-medium transition-colors"
          >
            ← 메인으로 돌아가기
          </button>

          {/* 지금까지 열심히 만든 핵심 컴포넌트 2개 렌더링! */}
          <SafeMap />
          <GapDashboard />
        </div>
      )}
    </div>
  )
}

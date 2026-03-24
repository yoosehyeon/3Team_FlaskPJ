export default function App() {
  return (
    <div className="min-h-screen bg-bg-light text-text-primary p-8 flex flex-col items-center justify-center space-y-4">
      <h1 className="text-4xl font-bold text-primary-main">모두의 길 (Modu-Gil)</h1>
      <p className="text-lg text-text-secondary">휠체어 통합 내비게이션 프론트엔드 인프라 구동 완료 🎉</p>
      
      {/* 12대 공통 CSS 변수 테스트 컴포넌트 */}
      <div className="flex gap-4 mt-6">
        <div className="w-24 h-24 rounded-base bg-safety-cyan flex items-center justify-center text-white shadow-card transition-all duration-fast hover:scale-105">
          안전 경로
        </div>
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
    </div>
  )
}

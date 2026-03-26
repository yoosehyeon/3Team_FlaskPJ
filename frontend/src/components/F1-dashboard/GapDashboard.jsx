import { motion, useMotionValue, useTransform, animate } from 'framer-motion';
import { useEffect } from 'react';
// 🚨 경로가 맞는지 확인해주세요! (예: '../../store/useMapStore')
import { useMapStore } from '../../store/useMapStore';

// 1. 숫자가 촤르륵 올라가는 애니메이션 부품
const CountUpNumber = ({ from = 0, to = 0, duration = 3 }) => {
  const count = useMotionValue(from);
  const rounded = useTransform(count, (latest) => Math.round(latest));

  useEffect(() => {
    const controls = animate(count, to, { duration });
    return () => controls.stop();
  }, [count, to, duration]);

  return <motion.span className="text-6xl font-bold">{rounded}</motion.span>;
};

// 2. 화면에 그려지는 메인 대시보드 (App.jsx가 애타게 찾던 그 녀석!)
export default function GapDashboard() {
  const { nondisabledTime, wheelchairTime } = useMapStore();

  // 데이터가 아직 없으면 안내 문구 표시
  if (!nondisabledTime || !wheelchairTime) {
    return (
      <div className="p-6 text-center text-gray-500 bg-white rounded-lg shadow-sm border mt-4">
        경로를 탐색하면 이곳에 소요 시간 비교가 나타납니다.
      </div>
    );
  }

  // 시간 및 비율 계산
  const ratio = (wheelchairTime / nondisabledTime).toFixed(2);
  const nondisabledMinutes = Math.round(nondisabledTime / 60);
  const wheelchairMinutes = Math.round(wheelchairTime / 60);

  return (
    <div className="bg-gradient-to-br from-red-50 to-orange-50 p-8 rounded-lg border border-red-200 mt-6 shadow-md">
      <h2 className="text-2xl font-bold text-center mb-8">같은 길, 다른 시간</h2>

      <div className="grid grid-cols-2 gap-8">
        {/* 비장애인 */}
        <div className="text-center">
          <p className="text-sm font-medium text-gray-600 mb-4">비장애인</p>
          <div className="bg-green-100 rounded-lg p-6 shadow-inner">
            <CountUpNumber from={0} to={nondisabledMinutes} duration={3} />
            <p className="text-lg text-green-700 mt-2">분</p>
          </div>
        </div>

        {/* 휠체어 이용자 */}
        <div className="text-center">
          <p className="text-sm font-medium text-gray-600 mb-4">휠체어 이용자</p>
          <div className="bg-red-100 rounded-lg p-6 shadow-inner">
            <CountUpNumber from={0} to={wheelchairMinutes} duration={3} />
            <p className="text-lg text-red-700 mt-2">분</p>
          </div>
        </div>
      </div>

      {/* 격차 강조 (3초 뒤에 뿅! 나타남) */}
      <motion.div
        className="mt-8 text-center"
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ delay: 3, type: 'spring', stiffness: 100 }}
      >
        <p className="text-3xl font-bold text-red-600">
          {ratio}배 더 걸립니다
        </p>
        <p className="text-sm text-gray-600 mt-2 font-medium">
          이동권은 아직도 불평등합니다
        </p>
      </motion.div>

      {/* 공유 버튼 */}
      <div className="mt-6 text-center">
        <button
          onClick={() => {
            const text = `같은 길, 다른 시간: ${nondisabledMinutes}분 vs ${wheelchairMinutes}분 (${ratio}배)`;
            if (navigator.share) {
              navigator.share({ title: '모두의 길', text });
            } else {
              alert('현재 브라우저에서는 공유하기 기능을 지원하지 않습니다.');
            }
          }}
          className="px-6 py-2 bg-blue-600 text-white rounded-full font-semibold hover:bg-blue-700 transition-colors shadow-sm"
        >
          공유하기
        </button>
      </div>
    </div>
  );
}

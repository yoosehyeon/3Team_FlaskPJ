/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // ✨ 유세현(PM)이 세팅한 공통 디자인 시스템 변수 연동 ✨
        // 사용 예: className="bg-primary-main text-text-primary"
        primary: {
          main: 'var(--color-primary-main)',
          light: 'var(--color-primary-light)',
          dark: 'var(--color-primary-dark)',
        },
        safety: {
          cyan: 'var(--color-safety-cyan)',     // 안전 경로 폴리라인(F2)용
        },
        danger: {
          red: 'var(--color-danger-red)',       // 에러 및 고장 알림(F3, F5)용
        },
        success: {
          green: 'var(--color-success-green)',    // 완료 및 배리어프리 정상 구역용
        },
        warning: {
          yellow: 'var(--color-warning-yellow)', // 주의 및 정비 중 표시
        },
        bg: {
          light: 'var(--color-bg-light)',
        },
        text: {
          primary: 'var(--color-text-primary)',
          secondary: 'var(--color-text-secondary)',
        }
      },
      borderRadius: {
        'base': 'var(--radius-base)',
      },
      boxShadow: {
        'card': 'var(--shadow-card)',
      },
      transitionDuration: {
        'fast': 'var(--transition-fast)',
      }
    },
  },
  plugins: [],
}

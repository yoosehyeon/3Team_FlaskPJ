/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#14b8a6", // 티록 색상 테마 예시
        dark: "#0f172a",
        light: "#f8fafc"
      }
    },
  },
  plugins: [],
}

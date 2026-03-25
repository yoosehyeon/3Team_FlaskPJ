import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import MapPage from './pages/Map'; // 새롭게 띄울 지도 전용 페이지
import './App.css';

/**
 * App 컴포넌트
 * 라우터를 통해 URL에 따라 알맞은 페이지를 보여줍니다.
 */
function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* 기본 접속 주소: 랜딩 페이지(Home) */}
        <Route path="/" element={<Home />} />

        {/* '지도 보기' 버튼 클릭 시 접속되는 주소: 지도 페이지 */}
        <Route path="/map" element={<MapPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;

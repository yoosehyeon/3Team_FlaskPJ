import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query' // 1. 필수 도구 임포트
import './index.css'
import App from "./App";

// 2. 새로운 통로(QueryClient) 생성
const queryClient = new QueryClient();

createRoot(document.getElementById('root')).render(
  <StrictMode>
    {/* 3. QueryClientProvider로 App을 감싸서 어디서든 React Query를 쓸 수 있게 함 */}
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </StrictMode>,
)

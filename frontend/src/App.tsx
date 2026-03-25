import { useEffect } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { useStore } from "./store/useStore";
import { supabase } from "./lib/supabase";
import Home from "./pages/Home";

function App() {
  const setUser = useStore((state) => state.setUser);

  useEffect(() => {
    // 세션 초기화 및 유저 정보 Zustand 저장
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null);
    });

    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        setUser(session?.user ?? null);
      }
    );

    return () => subscription.unsubscribe();
  }, [setUser]);

  return (
    <Router>
      <div className="min-h-screen relative w-full overflow-hidden text-slate-800 bg-slate-50">
        <Routes>
          <Route path="/" element={<Home />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;

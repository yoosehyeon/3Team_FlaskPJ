import { createClient } from '@supabase/supabase-js'

/**
 * ✨ 팀원 A: 유세현 PM 보완 - PRD v13.0 기술 스택의 핵심인 Supabase Auth 연동 클라이언트를 정의합니다.
 * 
 * 모든 프론트엔드 팀원(PL 김성익 등)은 이 공통 클라이언트를 import 하여 사용하며, 
 * 이를 통해 사용자 인증(JWT) 및 데이터 조회 시 일관된 보안 정책(RLS)을 유지할 수 있습니다.
 */

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

// 프로젝트 루트의 .env 파일에 URL과 KEY가 올바르게 입력되어야 작동합니다.
export const supabase = createClient(supabaseUrl, supabaseAnonKey)

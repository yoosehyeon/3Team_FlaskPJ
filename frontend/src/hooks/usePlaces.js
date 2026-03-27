import { useQuery } from "@tanstack/react-query";
import api from '../lib/api';
import { placesRequestSchema, placesResponseSchema } from '../schemas/placesSchema';

const fetchPlaces = async (lat, lng, radius = 300) => {
  // 1. 요청 파라미터 Zod 클라이언트 검증
  const validatedParams = placesRequestSchema.parse({ lat, lng, radius });

  const { data } = await api.get("/api/places", {
    params: validatedParams,
  });
  
  // 2. 서버 응답 데이터 Zod 스키마 검증 (예상치 못한 데이터 형태 방어)
  const validatedData = placesResponseSchema.parse(data);
  return validatedData;
};

export const usePlaces = (lat, lng, radius = 300) => {
  return useQuery({
    queryKey: ["places", lat, lng, radius],
    queryFn: () => fetchPlaces(lat, lng, radius),
    enabled: !!lat && !!lng,
    staleTime: 5 * 60 * 1000, // 5 minutes (캐싱)
    placeholderData: (previousData) => previousData, // 오프라인 fallback
  });
};

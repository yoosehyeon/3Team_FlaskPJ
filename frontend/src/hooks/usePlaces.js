import { useQuery } from "@tanstack/react-query";
import api from '../lib/api';

const fetchPlaces = async (lat, lng, radius = 300) => {
  const { data } = await api.get("/api/places", {
    params: { lat, lng, radius },
  });
  return data;
};

export const usePlaces = (lat, lng, radius = 300) => {
  return useQuery({
    queryKey: ["places", lat, lng, radius],
    queryFn: () => fetchPlaces(lat, lng, radius),
    enabled: !!lat && !!lng,
    staleTime: 5 * 60 * 1000, // 5 minutes
    placeholderData: (previousData) => previousData,
  });
};

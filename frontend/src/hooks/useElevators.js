import { useQuery } from "@tanstack/react-query";
import api from '../lib/api';

const fetchElevators = async () => {
  const { data } = await api.get("/api/elevators");
  return data;
};

export const useElevators = () => {
  return useQuery({
    queryKey: ["elevators"],
    queryFn: fetchElevators,
    staleTime: 60 * 1000, // 1 minute
  });
};

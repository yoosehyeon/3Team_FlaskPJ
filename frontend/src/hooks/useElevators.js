import { useQuery } from "@tanstack/react-query";
import axios from "axios";

const fetchElevators = async () => {
  const { data } = await axios.get("/api/elevators");
  return data;
};

export const useElevators = () => {
  return useQuery({
    queryKey: ["elevators"],
    queryFn: fetchElevators,
    staleTime: 60 * 1000, // 1 minute
  });
};

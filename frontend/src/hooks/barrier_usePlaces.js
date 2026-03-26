import { useQuery } from '@tanstack/react-query';
import useUIStore from '../store/useUIStore';

export const useBarrierPlaces = (lat, lng, radius = 300) => {
  const setBarrierPlaces = useUIStore((state) => state.setBarrierPlaces);

  return useQuery({
    queryKey: ['barrierPlaces', lat, lng, radius],
    queryFn: async () => {
      if (!lat || !lng) return [];
      
      const response = await fetch(`http://localhost:5000/api/barrier/places?lat=${lat}&lng=${lng}&radius=${radius}`);
      if (!response.ok) {
        throw new Error('Failed to fetch barrier-free places');
      }
      const data = await response.json();
      
      if (data.status === 'success') {
        setBarrierPlaces(data.data);
        return data.data;
      }
      return [];
    },
    enabled: !!lat && !!lng,
    staleTime: 1000 * 60 * 5, // 5 minutes cache
  });
};

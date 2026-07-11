import { useQuery } from '@tanstack/react-query';
import { TaskResponse } from '../types';
import { campaignService } from '../services/api';

export const useTaskPolling = (taskId: string | null, interval = 1000) => {
  const query = useQuery<TaskResponse, Error>({
    queryKey: ['task', taskId],
    queryFn: () => campaignService.getTaskStatus(taskId!),
    enabled: !!taskId,
    refetchInterval: (query) => {
      const data = query.state.data;
      if (!data) return interval;
      if (data.status === 'completed' || data.status === 'failed') return false;
      return interval;
    },
    staleTime: 0,
    gcTime: 0,
  });

  return {
    status: query.data || null,
    loading: query.isLoading && query.fetchStatus !== 'idle',
    error: query.error?.message || null,
  };
};

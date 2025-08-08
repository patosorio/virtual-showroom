"use client";

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import { UserProfile } from '@/types/auth';
import toast from 'react-hot-toast';

export function useUserProfile() {
  return useQuery({
    queryKey: ['auth', 'profile'],
    queryFn: async (): Promise<UserProfile> => {
      const response = await apiClient.get('/auth/me');
      return response.data;
    },
    retry: false, // Don't retry auth requests
  });
}

export function useUpdateProfile() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: Partial<UserProfile>) => {
      const response = await apiClient.put('/auth/me', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['auth', 'profile'] });
      toast.success('Profile updated successfully!');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to update profile');
    },
  });
}
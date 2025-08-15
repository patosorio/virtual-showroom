"use client";

import { 
  useQuery, 
  useMutation, 
  useQueryClient,
  UseQueryOptions,
  UseMutationOptions,
} from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { collectionsApi } from '@/lib/api/collections';
import type {
  CollectionResponse,
  CollectionsListResponse,
  CollectionCreate,
  CollectionUpdate,
  CollectionPublishRequest,
  CollectionAnalytics,
  FeaturedCollectionsResponse,
  SearchCollectionsResponse,
  CollectionsListParams,
  SearchCollectionsParams,
} from '@/types/collections';

// Query Keys
export const collectionsKeys = {
  all: ['collections'] as const,
  lists: () => [...collectionsKeys.all, 'list'] as const,
  list: (params: CollectionsListParams) => [...collectionsKeys.lists(), params] as const,
  details: () => [...collectionsKeys.all, 'detail'] as const,
  detail: (id: string) => [...collectionsKeys.details(), id] as const,
  detailBySlug: (slug: string) => [...collectionsKeys.details(), 'slug', slug] as const,
  featured: () => [...collectionsKeys.all, 'featured'] as const,
  search: (params: SearchCollectionsParams) => [...collectionsKeys.all, 'search', params] as const,
  analytics: (id: string) => [...collectionsKeys.all, 'analytics', id] as const,
};

/**
 * Hook to list collections with pagination and filtering
 */
export function useCollections(
  params: CollectionsListParams = {},
  options?: Omit<UseQueryOptions<CollectionsListResponse>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: collectionsKeys.list(params),
    queryFn: () => collectionsApi.list(params),
    ...options,
  });
}

/**
 * Hook to get a single collection by ID
 */
export function useCollection(
  id: string,
  options?: Omit<UseQueryOptions<CollectionResponse>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: collectionsKeys.detail(id),
    queryFn: () => collectionsApi.getById(id),
    enabled: !!id,
    ...options,
  });
}

/**
 * Hook to get a single collection by slug
 */
export function useCollectionBySlug(
  slug: string,
  options?: Omit<UseQueryOptions<CollectionResponse>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: collectionsKeys.detailBySlug(slug),
    queryFn: () => collectionsApi.getBySlug(slug),
    enabled: !!slug,
    ...options,
  });
}

/**
 * Hook to get featured collections
 */
export function useFeaturedCollections(
  limit: number = 6,
  options?: Omit<UseQueryOptions<FeaturedCollectionsResponse>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: collectionsKeys.featured(),
    queryFn: () => collectionsApi.getFeatured(limit),
    ...options,
  });
}

/**
 * Hook to search collections
 */
export function useSearchCollections(
  params: SearchCollectionsParams,
  options?: Omit<UseQueryOptions<SearchCollectionsResponse>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: collectionsKeys.search(params),
    queryFn: () => collectionsApi.search(params),
    enabled: !!params.q && params.q.length >= 2,
    ...options,
  });
}

/**
 * Hook to get collection analytics
 */
export function useCollectionAnalytics(
  id: string,
  options?: Omit<UseQueryOptions<CollectionAnalytics>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: collectionsKeys.analytics(id),
    queryFn: () => collectionsApi.getAnalytics(id),
    enabled: !!id,
    ...options,
  });
}

/**
 * Hook to create a new collection
 */
export function useCreateCollection(
  options?: UseMutationOptions<CollectionResponse, Error, CollectionCreate>
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: collectionsApi.create,
    onSuccess: (data) => {
      // Invalidate and refetch collections list
      queryClient.invalidateQueries({ queryKey: collectionsKeys.lists() });
      queryClient.setQueryData(collectionsKeys.detail(data.id), data);
      toast.success('Collection created successfully!');
    },
    onError: (error: any) => {
      // Handle validation errors
      if (error.response?.status === 422) {
        const errors = error.response.data.errors;
        if (errors && Array.isArray(errors)) {
          errors.forEach(err => {
            const field = err.loc[err.loc.length - 1];
            const message = err.msg;
            toast.error(`${field}: ${message}`);
          });
        } else {
          toast.error('Validation failed. Please check your input.');
        }
      } else {
        toast.error(error.response?.data?.detail || 'Failed to create collection');
      }
    },
    ...options,
  });
}

/**
 * Hook to update an existing collection
 */
export function useUpdateCollection(
  options?: UseMutationOptions<CollectionResponse, Error, { id: string; data: CollectionUpdate }>
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }) => collectionsApi.update(id, data),
    onSuccess: (data, variables) => {
      // Update the collection in cache
      queryClient.setQueryData(collectionsKeys.detail(variables.id), data);
      // Invalidate lists to update any summary data
      queryClient.invalidateQueries({ queryKey: collectionsKeys.lists() });
      toast.success('Collection updated successfully!');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to update collection');
    },
    ...options,
  });
}

/**
 * Hook to delete a collection
 */
export function useDeleteCollection(
  options?: UseMutationOptions<void, Error, string>
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: collectionsApi.delete,
    onSuccess: (_, id) => {
      // Remove from cache
      queryClient.removeQueries({ queryKey: collectionsKeys.detail(id) });
      // Invalidate lists
      queryClient.invalidateQueries({ queryKey: collectionsKeys.lists() });
      toast.success('Collection deleted successfully!');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to delete collection');
    },
    ...options,
  });
}

/**
 * Hook to publish/unpublish a collection
 */
export function usePublishCollection(
  options?: UseMutationOptions<CollectionResponse, Error, { id: string; data: CollectionPublishRequest }>
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }) => collectionsApi.publish(id, data),
    onSuccess: (data, variables) => {
      // Update the collection in cache
      queryClient.setQueryData(collectionsKeys.detail(variables.id), data);
      // Invalidate lists to update publication status
      queryClient.invalidateQueries({ queryKey: collectionsKeys.lists() });
      const action = variables.data.publish ? 'published' : 'unpublished';
      toast.success(`Collection ${action} successfully!`);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to update publication status');
    },
    ...options,
  });
}
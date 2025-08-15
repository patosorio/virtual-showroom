/**
 * Collections API Client
 * 
 * Handles all API calls for Collections endpoints.
 * Matches the backend routes in backend/app/api/routes/collections.py
 */

import { apiClient } from './client';
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

const COLLECTIONS_BASE_URL = '/collections';

/**
 * Collections API client
 */
export const collectionsApi = {
  /**
   * List collections with pagination and filtering
   * GET /collections/
   */
  async list(params: CollectionsListParams = {}): Promise<CollectionsListResponse> {
    const searchParams = new URLSearchParams();
    
    // Add pagination params
    if (params.skip !== undefined) searchParams.append('skip', params.skip.toString());
    if (params.limit !== undefined) searchParams.append('limit', params.limit.toString());
    
    // Add filter params
    if (params.season) searchParams.append('season', params.season);
    if (params.year !== undefined) searchParams.append('year', params.year.toString());
    if (params.status) searchParams.append('collection_status', params.status);
    if (params.is_published !== undefined) searchParams.append('is_published', params.is_published.toString());
    if (params.query) searchParams.append('query', params.query);
    if (params.has_products !== undefined) searchParams.append('has_products', params.has_products.toString());

    const url = `${COLLECTIONS_BASE_URL}/${searchParams.toString() ? `?${searchParams.toString()}` : ''}`;
    const response = await apiClient.get<CollectionsListResponse>(url);
    return response.data;
  },

  /**
   * Get a single collection by ID
   * GET /collections/{collection_id}
   */
  async getById(id: string): Promise<CollectionResponse> {
    const response = await apiClient.get<CollectionResponse>(`${COLLECTIONS_BASE_URL}/${id}`);
    return response.data;
  },

  /**
   * Get a single collection by slug
   * GET /collections/slug/{slug}
   */
  async getBySlug(slug: string): Promise<CollectionResponse> {
    const response = await apiClient.get<CollectionResponse>(`${COLLECTIONS_BASE_URL}/slug/${slug}`);
    return response.data;
  },

  /**
   * Create a new collection (admin only)
   * POST /collections/
   */
  async create(data: CollectionCreate): Promise<CollectionResponse> {
    const response = await apiClient.post<CollectionResponse>(COLLECTIONS_BASE_URL, data);
    return response.data;
  },

  /**
   * Update an existing collection (admin only)
   * PUT /collections/{collection_id}
   */
  async update(id: string, data: CollectionUpdate): Promise<CollectionResponse> {
    const response = await apiClient.put<CollectionResponse>(`${COLLECTIONS_BASE_URL}/${id}`, data);
    return response.data;
  },

  /**
   * Delete a collection (admin only)
   * DELETE /collections/{collection_id}
   */
  async delete(id: string): Promise<void> {
    await apiClient.delete(`${COLLECTIONS_BASE_URL}/${id}`);
  },

  /**
   * Publish/unpublish a collection (admin only)
   * POST /collections/{collection_id}/publish
   */
  async publish(id: string, data: CollectionPublishRequest): Promise<CollectionResponse> {
    const response = await apiClient.post<CollectionResponse>(
      `${COLLECTIONS_BASE_URL}/${id}/publish`,
      data
    );
    return response.data;
  },

  /**
   * Get collection analytics (admin only)
   * GET /collections/{collection_id}/analytics
   */
  async getAnalytics(id: string): Promise<CollectionAnalytics> {
    const response = await apiClient.get<CollectionAnalytics>(`${COLLECTIONS_BASE_URL}/${id}/analytics`);
    return response.data;
  },

  /**
   * Get featured collections
   * GET /collections/featured/
   */
  async getFeatured(limit: number = 6): Promise<FeaturedCollectionsResponse> {
    const response = await apiClient.get<FeaturedCollectionsResponse>(
      `${COLLECTIONS_BASE_URL}/featured/?limit=${limit}`
    );
    return response.data;
  },

  /**
   * Search collections
   * GET /collections/search/
   */
  async search(params: SearchCollectionsParams): Promise<SearchCollectionsResponse> {
    const searchParams = new URLSearchParams();
    
    // Required param
    searchParams.append('q', params.q);
    
    // Optional params
    if (params.published_only !== undefined) {
      searchParams.append('published_only', params.published_only.toString());
    }
    if (params.skip !== undefined) {
      searchParams.append('skip', params.skip.toString());
    }
    if (params.limit !== undefined) {
      searchParams.append('limit', params.limit.toString());
    }

    const response = await apiClient.get<SearchCollectionsResponse>(
      `${COLLECTIONS_BASE_URL}/search/?${searchParams.toString()}`
    );
    return response.data;
  },
};

export default collectionsApi;
/**
 * Collection Types - Matching Backend Schemas
 * 
 * These types match exactly with the backend Collection schemas
 * from backend/app/schemas/collection.py
 */

// Base types matching backend schemas
export interface CollectionResponse {
  // From BaseResponseSchema
  id: string;
  created_at: string;
  updated_at: string;
  created_by?: string;
  updated_by?: string;
  is_deleted: boolean;
  deleted_at?: string;
  notes?: string;

  // From CollectionBase
  name: string;
  slug: string;
  season: string;
  year: number;
  description?: string;
  short_description?: string;
  order_start_date?: string;
  order_end_date?: string;
  seo_title?: string;
  seo_description?: string;
  metadata?: Record<string, any>;

  // From CollectionResponse
  status: string;
  is_published: boolean;
  product_count: number;
  is_order_period_active: boolean;
  full_name: string;

  // Optional nested relationships (from backend)
  products?: ProductSummaryResponse[];
  files?: FileResponse[];
}

export interface CollectionSummary {
  id: string;
  name: string;
  slug: string;
  season: string;
  year: number;
  status: string;
  is_published: boolean;
  product_count: number;
  full_name: string;
}

export interface CollectionCreate {
  // From CollectionBase
  name: string;
  slug: string;
  season: string;
  year: number;
  description?: string;
  short_description?: string;
  order_start_date?: string;
  order_end_date?: string;
  seo_title?: string;
  seo_description?: string;
  metadata?: Record<string, any>;

  // From CollectionCreate
  status?: string; // defaults to 'draft'
  is_published?: boolean; // defaults to false
  notes?: string;
}

export interface CollectionUpdate {
  name?: string;
  slug?: string;
  season?: string;
  year?: number;
  description?: string;
  short_description?: string;
  order_start_date?: string;
  order_end_date?: string;
  status?: string;
  is_published?: boolean;
  seo_title?: string;
  seo_description?: string;
  metadata?: Record<string, any>;
  notes?: string;
}

export interface CollectionListFilters {
  season?: string;
  year?: number;
  status?: string;
  is_published?: boolean;
  query?: string;
  has_products?: boolean;
}

export interface CollectionPublishRequest {
  publish: boolean;
  seo_title?: string;
  seo_description?: string;
}

export interface CollectionAnalytics {
  total_products: number;
  products_by_category: Record<string, number>;
  products_by_status: Record<string, number>;
  average_price?: number;
  price_range: Record<string, number>;
  last_updated?: string;
}

// Pagination types matching backend
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
  has_next: boolean;
  has_prev: boolean;
  page: number;
  total_pages: number;
}

// Placeholder types for nested relationships (basic structure)
export interface ProductSummaryResponse {
  id: string;
  name: string;
  // Add more fields as needed when implementing products
}

export interface FileResponse {
  id: string;
  filename: string;
  original_filename: string;
  content_type: string;
  size: number;
  url: string;
  metadata?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

// API Response types
export type CollectionsListResponse = PaginatedResponse<CollectionResponse>;
export type FeaturedCollectionsResponse = CollectionResponse[];
export type SearchCollectionsResponse = CollectionResponse[];

// Query parameters for API calls
export interface CollectionsListParams extends CollectionListFilters {
  skip?: number;
  limit?: number;
}

export interface SearchCollectionsParams {
  q: string;
  published_only?: boolean;
  skip?: number;
  limit?: number;
}

// Status enums matching backend
export const COLLECTION_STATUS = ['draft', 'active', 'archived'] as const;
export const SEASONS = ['Spring', 'Summer', 'Fall', 'Winter'] as const;

export type CollectionStatus = typeof COLLECTION_STATUS[number];
export type Season = typeof SEASONS[number];

// Frontend Collection interface - minimal transform from backend
// Only transforms field names, keeps types simple
export interface Collection {
  id: string;
  name: string;
  season: string;
  year: number;
  orderDates: {
    start: string;
    end: string;
  };
  description: string;
  products: any[]; // Will be empty until Products API is implemented
}
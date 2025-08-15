/**
 * Collection Data Transformers
 * 
 * Transforms backend Collection data to frontend Collection interface
 * Handles differences between backend schema and frontend component expectations
 */

import type { CollectionResponse, Collection } from '@/types/collections';

/**
 * Transform backend CollectionResponse to frontend Collection interface
 */
export function transformCollectionResponse(backendCollection: CollectionResponse): Collection {
  return {
    id: backendCollection.id,
    name: backendCollection.name,
    season: backendCollection.season,
    year: backendCollection.year,
    orderDates: {
      start: formatOrderDate(backendCollection.order_start_date),
      end: formatOrderDate(backendCollection.order_end_date),
    },
    description: backendCollection.description || backendCollection.short_description || '',
    // For now, return empty products array until Products API is implemented
    // Later this will transform backendCollection.products when available
    products: [],
  };
}

/**
 * Transform a list of backend collections to frontend format
 */
export function transformCollectionsList(backendCollections: CollectionResponse[]): Collection[] {
  return backendCollections.map(transformCollectionResponse);
}

/**
 * Format backend date string to frontend display format
 * Backend: "2024-10-15" (ISO date)
 * Frontend: "15th October" or "15th October 2024"
 */
function formatOrderDate(dateString?: string): string {
  if (!dateString) return '';
  
  try {
    const date = new Date(dateString);
    
    // Check if date is valid
    if (isNaN(date.getTime())) return dateString;
    
    const day = date.getDate();
    const month = date.toLocaleString('en-US', { month: 'long' });
    const year = date.getFullYear();
    
    // Add ordinal suffix to day
    const getOrdinalSuffix = (day: number): string => {
      if (day > 3 && day < 21) return 'th';
      switch (day % 10) {
        case 1: return 'st';
        case 2: return 'nd';
        case 3: return 'rd';
        default: return 'th';
      }
    };
    
    const ordinalDay = `${day}${getOrdinalSuffix(day)}`;
    
    // For current year, omit year. For other years, include it.
    const currentYear = new Date().getFullYear();
    if (year === currentYear) {
      return `${ordinalDay} ${month}`;
    } else {
      return `${ordinalDay} ${month} ${year}`;
    }
  } catch (error) {
    // If date parsing fails, return original string
    return dateString;
  }
}

/**
 * Transform frontend Collection to backend CollectionCreate format
 * Useful for create/update operations
 */
export function transformToCollectionCreate(frontendCollection: Partial<Collection>): any {
  return {
    name: frontendCollection.name,
    // Generate slug from name if not provided
    slug: generateSlugFromName(frontendCollection.name || ''),
    season: frontendCollection.season,
    year: frontendCollection.year,
    description: frontendCollection.description,
    order_start_date: frontendCollection.orderDates?.start 
      ? parseOrderDate(frontendCollection.orderDates.start) 
      : undefined,
    order_end_date: frontendCollection.orderDates?.end 
      ? parseOrderDate(frontendCollection.orderDates.end) 
      : undefined,
  };
}

/**
 * Parse frontend order date format back to ISO date string
 * Frontend: "15th October 2024" or "15th October"
 * Backend: "2024-10-15"
 */
function parseOrderDate(dateString: string): string | undefined {
  if (!dateString) return undefined;
  
  try {
    // Try to parse the formatted date back to ISO format
    // This is a simplified implementation - in production you might want more robust parsing
    const currentYear = new Date().getFullYear();
    
    // Remove ordinal suffixes (st, nd, rd, th)
    const cleanDate = dateString.replace(/(\d+)(st|nd|rd|th)/, '$1');
    
    // If no year specified, add current year
    const dateWithYear = cleanDate.includes(currentYear.toString()) 
      ? cleanDate 
      : `${cleanDate} ${currentYear}`;
    
    const parsed = new Date(dateWithYear);
    
    if (isNaN(parsed.getTime())) return undefined;
    
    return parsed.toISOString().split('T')[0]; // Return YYYY-MM-DD format
  } catch (error) {
    return undefined;
  }
}

/**
 * Generate a URL-friendly slug from a collection name
 */
function generateSlugFromName(name: string): string {
  return name
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, '') // Remove special characters
    .replace(/[\s_-]+/g, '-') // Replace spaces and underscores with hyphens
    .replace(/^-+|-+$/g, ''); // Remove leading/trailing hyphens
}

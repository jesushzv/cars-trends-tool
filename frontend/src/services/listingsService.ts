import { apiClient } from './apiClient';

interface ListingFilters {
  platform?: string;
  make?: string;
  model?: string;
  min_price?: number;
  max_price?: number;
  min_year?: number;
  max_year?: number;
  condition?: string;
  days_back?: number;
}

class ListingsService {
  async getListings(filters: ListingFilters = {}) {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== '') {
        params.append(key, value.toString());
      }
    });

    const response = await apiClient.get(`/listings?${params}`);
    return response.data;
  }

  async getListingById(id: string) {
    const response = await apiClient.get(`/listings/${id}`);
    return response.data;
  }

  async getListingsByPlatform(platform: string, daysBack: number = 30) {
    const response = await apiClient.get(`/listings/platform/${platform}?days_back=${daysBack}`);
    return response.data;
  }

  async getTopListingsByEngagement(limit: number = 20, daysBack: number = 30) {
    const response = await apiClient.get(`/listings/top/engagement?limit=${limit}&days_back=${daysBack}`);
    return response.data;
  }

  async getListingsSummary(daysBack: number = 30) {
    const response = await apiClient.get(`/listings/stats/summary?days_back=${daysBack}`);
    return response.data;
  }
}

export const listingsService = new ListingsService();

import { apiClient } from './apiClient';

class TrendsService {
  async getTrends(daysBack: number = 30) {
    const response = await apiClient.get(`/trends?days_back=${daysBack}`);
    return response.data;
  }

  async getTrendsByMakeModel(make: string, model: string, daysBack: number = 30) {
    const response = await apiClient.get(`/trends/${make}/${model}?days_back=${daysBack}`);
    return response.data;
  }

  async getTopTrendsByEngagement(limit: number = 20, daysBack: number = 30) {
    const response = await apiClient.get(`/trends/top/engagement?limit=${limit}&days_back=${daysBack}`);
    return response.data;
  }

  async getTrendsSummary(daysBack: number = 30) {
    const response = await apiClient.get(`/trends/stats/summary?days_back=${daysBack}`);
    return response.data;
  }
}

export const trendsService = new TrendsService();

import { apiClient } from './apiClient';

class AnalyticsService {
  async getDashboardSummary(daysBack: number = 30) {
    const response = await apiClient.get(`/analytics/dashboard-summary?days_back=${daysBack}`);
    return response.data;
  }

  async getTopCarsByEngagement(limit: number = 20, daysBack: number = 30) {
    const response = await apiClient.get(`/analytics/top-cars?limit=${limit}&days_back=${daysBack}`);
    return response.data;
  }

  async getPriceTrends(make?: string, model?: string, daysBack: number = 30) {
    const params = new URLSearchParams({ days_back: daysBack.toString() });
    if (make) params.append('make', make);
    if (model) params.append('model', model);
    
    const response = await apiClient.get(`/analytics/price-trends?${params}`);
    return response.data;
  }

  async getMarketShare(daysBack: number = 30, groupBy: 'make' | 'model' = 'make') {
    const response = await apiClient.get(`/analytics/market-share?days_back=${daysBack}&by=${groupBy}`);
    return response.data;
  }

  async getEngagementAnalysis(daysBack: number = 30) {
    const response = await apiClient.get(`/analytics/engagement-analysis?days_back=${daysBack}`);
    return response.data;
  }

  async getListingFrequency(make?: string, model?: string, daysBack: number = 30) {
    const params = new URLSearchParams({ days_back: daysBack.toString() });
    if (make) params.append('make', make);
    if (model) params.append('model', model);
    
    const response = await apiClient.get(`/analytics/listing-frequency?${params}`);
    return response.data;
  }
}

export const analyticsService = new AnalyticsService();

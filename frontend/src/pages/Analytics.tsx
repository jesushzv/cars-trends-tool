import React from 'react';
import { useQuery } from 'react-query';
import { analyticsService } from '../services/analyticsService';
import LoadingSpinner from '../components/LoadingSpinner';
import EngagementAnalysis from '../components/EngagementAnalysis';

const Analytics: React.FC = () => {
  const { data: analytics, isLoading, error } = useQuery(
    'analytics',
    () => analyticsService.getEngagementAnalysis(30),
    {
      refetchInterval: 5 * 60 * 1000, // Refetch every 5 minutes
    }
  );

  if (isLoading) {
    return <LoadingSpinner className="min-h-96" />;
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">Failed to load analytics data</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
        <p className="text-gray-600">Detailed engagement and market analysis</p>
      </div>

      {/* Analytics Content */}
      <div className="chart-container">
        <EngagementAnalysis data={analytics} />
      </div>
    </div>
  );
};

export default Analytics;

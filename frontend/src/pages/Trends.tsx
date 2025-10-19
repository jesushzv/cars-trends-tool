import React from 'react';
import { useQuery } from 'react-query';
import { trendsService } from '../services/trendsService';
import LoadingSpinner from '../components/LoadingSpinner';
import TrendsChart from '../components/TrendsChart';

const Trends: React.FC = () => {
  const { data: trends, isLoading, error } = useQuery(
    'trends',
    () => trendsService.getTrends(30),
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
        <p className="text-red-600">Failed to load trends data</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Market Trends</h1>
        <p className="text-gray-600">Track car market trends over time</p>
      </div>

      {/* Trends Chart */}
      <div className="chart-container">
        <TrendsChart data={trends || []} />
      </div>
    </div>
  );
};

export default Trends;

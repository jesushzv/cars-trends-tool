import React from 'react';
import { useQuery } from 'react-query';
import { 
  ChartBarIcon, 
  DocumentTextIcon, 
  EyeIcon, 
  HeartIcon,
  ChatBubbleLeftIcon,
  BookmarkIcon,
  ShareIcon
} from '@heroicons/react/24/outline';
import { analyticsService } from '../services/analyticsService';
import LoadingSpinner from './LoadingSpinner';
import StatCard from './StatCard';
import TopCarsChart from './TopCarsChart';
import PriceTrendsChart from './PriceTrendsChart';
import MarketShareChart from './MarketShareChart';

const Dashboard: React.FC = () => {
  const { data: dashboardData, isLoading, error } = useQuery(
    'dashboard-summary',
    () => analyticsService.getDashboardSummary(30),
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
        <p className="text-red-600">Failed to load dashboard data</p>
      </div>
    );
  }

  const summary = dashboardData?.overall_metrics || {};
  const topCars = dashboardData?.top_cars || [];
  const priceTrends = dashboardData?.price_trends || [];
  const marketShare = dashboardData?.market_share || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600">Overview of car market trends in Tijuana, Mexico</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Listings"
          value={summary.total_listings?.toLocaleString() || '0'}
          icon={DocumentTextIcon}
          color="blue"
        />
        <StatCard
          title="Total Views"
          value={summary.total_views?.toLocaleString() || '0'}
          icon={EyeIcon}
          color="green"
        />
        <StatCard
          title="Total Likes"
          value={summary.total_likes?.toLocaleString() || '0'}
          icon={HeartIcon}
          color="red"
        />
        <StatCard
          title="Total Comments"
          value={summary.total_comments?.toLocaleString() || '0'}
          icon={ChatBubbleLeftIcon}
          color="purple"
        />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Cars by Engagement */}
        <div className="chart-container">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Top Cars by Engagement</h3>
            <ChartBarIcon className="h-5 w-5 text-gray-400" />
          </div>
          <TopCarsChart data={topCars.slice(0, 10)} />
        </div>

        {/* Market Share */}
        <div className="chart-container">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Market Share by Brand</h3>
            <ChartBarIcon className="h-5 w-5 text-gray-400" />
          </div>
          <MarketShareChart data={marketShare.slice(0, 8)} />
        </div>
      </div>

      {/* Price Trends */}
      <div className="chart-container">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Price Trends (Last 30 Days)</h3>
          <ChartBarIcon className="h-5 w-5 text-gray-400" />
        </div>
        <PriceTrendsChart data={priceTrends} />
      </div>

      {/* Top Cars Table */}
      <div className="chart-container">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Top Performing Cars</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="table">
            <thead className="table-header">
              <tr>
                <th className="table-header-cell">Rank</th>
                <th className="table-header-cell">Make & Model</th>
                <th className="table-header-cell">Listings</th>
                <th className="table-header-cell">Avg Price</th>
                <th className="table-header-cell">Views</th>
                <th className="table-header-cell">Likes</th>
                <th className="table-header-cell">Comments</th>
                <th className="table-header-cell">Engagement Score</th>
              </tr>
            </thead>
            <tbody className="table-body">
              {topCars.slice(0, 10).map((car, index) => (
                <tr key={`${car.make}-${car.model}`} className="table-row">
                  <td className="table-cell">
                    <span className="badge badge-primary">#{index + 1}</span>
                  </td>
                  <td className="table-cell font-medium">
                    {car.make} {car.model}
                  </td>
                  <td className="table-cell">{car.total_listings}</td>
                  <td className="table-cell">
                    {car.avg_price ? `$${car.avg_price.toLocaleString()}` : 'N/A'}
                  </td>
                  <td className="table-cell">{car.total_views.toLocaleString()}</td>
                  <td className="table-cell">{car.total_likes.toLocaleString()}</td>
                  <td className="table-cell">{car.total_comments.toLocaleString()}</td>
                  <td className="table-cell">
                    <span className="font-semibold text-blue-600">
                      {car.engagement_score.toLocaleString()}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface EngagementAnalysisProps {
  data: {
    platform_analysis: Array<{
      platform: string;
      total_listings: number;
      avg_views: number;
      avg_likes: number;
      avg_comments: number;
      avg_engagement_score: number;
    }>;
    overall_metrics: {
      total_listings: number;
      total_views: number;
      total_likes: number;
      total_comments: number;
      total_saves: number;
      total_shares: number;
    };
  };
}

const EngagementAnalysis: React.FC<EngagementAnalysisProps> = ({ data }) => {
  if (!data) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No engagement data available</p>
      </div>
    );
  }

  const platformData = {
    labels: data.platform_analysis.map(p => p.platform),
    datasets: [
      {
        label: 'Avg Views',
        data: data.platform_analysis.map(p => p.avg_views),
        backgroundColor: 'rgba(59, 130, 246, 0.8)',
        borderColor: 'rgba(59, 130, 246, 1)',
        borderWidth: 1,
      },
      {
        label: 'Avg Likes',
        data: data.platform_analysis.map(p => p.avg_likes),
        backgroundColor: 'rgba(34, 197, 94, 0.8)',
        borderColor: 'rgba(34, 197, 94, 1)',
        borderWidth: 1,
      },
      {
        label: 'Avg Comments',
        data: data.platform_analysis.map(p => p.avg_comments),
        backgroundColor: 'rgba(239, 68, 68, 0.8)',
        borderColor: 'rgba(239, 68, 68, 1)',
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      tooltip: {
        callbacks: {
          afterLabel: function(context: any) {
            const platform = data.platform_analysis[context.dataIndex];
            return [
              `Total Listings: ${platform.total_listings}`,
              `Avg Engagement Score: ${platform.avg_engagement_score.toFixed(2)}`,
            ];
          },
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: function(value: any) {
            return value.toFixed(1);
          },
        },
      },
    },
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Platform Engagement Analysis</h3>
        <div className="chart-responsive">
          <Bar data={platformData} options={options} />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="stat-card">
          <h4 className="text-sm font-medium text-gray-500 uppercase tracking-wide">Total Listings</h4>
          <p className="text-2xl font-bold text-gray-900">{data.overall_metrics.total_listings.toLocaleString()}</p>
        </div>
        <div className="stat-card">
          <h4 className="text-sm font-medium text-gray-500 uppercase tracking-wide">Total Views</h4>
          <p className="text-2xl font-bold text-gray-900">{data.overall_metrics.total_views.toLocaleString()}</p>
        </div>
        <div className="stat-card">
          <h4 className="text-sm font-medium text-gray-500 uppercase tracking-wide">Total Likes</h4>
          <p className="text-2xl font-bold text-gray-900">{data.overall_metrics.total_likes.toLocaleString()}</p>
        </div>
        <div className="stat-card">
          <h4 className="text-sm font-medium text-gray-500 uppercase tracking-wide">Total Comments</h4>
          <p className="text-2xl font-bold text-gray-900">{data.overall_metrics.total_comments.toLocaleString()}</p>
        </div>
        <div className="stat-card">
          <h4 className="text-sm font-medium text-gray-500 uppercase tracking-wide">Total Saves</h4>
          <p className="text-2xl font-bold text-gray-900">{data.overall_metrics.total_saves.toLocaleString()}</p>
        </div>
        <div className="stat-card">
          <h4 className="text-sm font-medium text-gray-500 uppercase tracking-wide">Total Shares</h4>
          <p className="text-2xl font-bold text-gray-900">{data.overall_metrics.total_shares.toLocaleString()}</p>
        </div>
      </div>
    </div>
  );
};

export default EngagementAnalysis;

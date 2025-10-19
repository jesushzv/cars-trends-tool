import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface TrendsChartProps {
  data: Array<{
    make: string;
    model: string;
    date: string;
    total_listings: number;
    avg_price: number;
    engagement_score: number;
  }>;
}

const TrendsChart: React.FC<TrendsChartProps> = ({ data }) => {
  // Group data by make/model and create datasets
  const groupedData = data.reduce((acc, item) => {
    const key = `${item.make} ${item.model}`;
    if (!acc[key]) {
      acc[key] = [];
    }
    acc[key].push(item);
    return acc;
  }, {} as Record<string, typeof data>);

  const colors = [
    'rgba(59, 130, 246, 1)',
    'rgba(34, 197, 94, 1)',
    'rgba(239, 68, 68, 1)',
    'rgba(168, 85, 247, 1)',
    'rgba(245, 158, 11, 1)',
  ];

  const datasets = Object.entries(groupedData).slice(0, 5).map(([key, items], index) => ({
    label: key,
    data: items.map(item => item.engagement_score),
    borderColor: colors[index % colors.length],
    backgroundColor: colors[index % colors.length].replace('1)', '0.1)'),
    tension: 0.4,
  }));

  const chartData = {
    labels: [...new Set(data.map(item => new Date(item.date).toLocaleDateString()))],
    datasets,
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
            const item = data.find(d => 
              d.make === context.dataset.label.split(' ')[0] && 
              d.model === context.dataset.label.split(' ')[1] &&
              new Date(d.date).toLocaleDateString() === context.label
            );
            if (item) {
              return [
                `Listings: ${item.total_listings}`,
                `Avg Price: $${item.avg_price?.toLocaleString() || 'N/A'}`,
              ];
            }
            return [];
          },
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: function(value: any) {
            return value.toLocaleString();
          },
        },
      },
      x: {
        ticks: {
          maxRotation: 45,
          minRotation: 45,
        },
      },
    },
  };

  return (
    <div className="chart-responsive">
      <Line data={chartData} options={options} />
    </div>
  );
};

export default TrendsChart;
